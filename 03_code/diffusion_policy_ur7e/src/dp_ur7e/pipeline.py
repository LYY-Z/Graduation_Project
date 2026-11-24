"""Explicit capture, shadow, preview and guarded execution workflows."""

from __future__ import annotations

import time
import numpy as np
from .inference.policy import load_policy, predict, validate_predictions
from .recording import RunWriter, environment_versions, preview_actions
from .hardware.observations import SensorSession
import contextlib
from dataclasses import asdict
from .control.robot import (
    GuardedRobot,
    connect_control,
    dashboard_status,
    read_feedback,
    require_dashboard_ready,
)
from .control.safety import ActionGuard, MotionLimits


def run_capture_shadow(cfg, *, inference: bool):
    details, policy = None, None
    if inference:
        import torch

        torch.manual_seed(int(cfg["inference"]["seed"]))
        np.random.seed(int(cfg["inference"]["seed"]))
        policy, details = load_policy(cfg)
    metadata = {
        "mode": "shadow" if inference else "capture",
        "execution_enabled": False,
        "environment": environment_versions(),
        "platform_config": cfg,
        "model": details,
        "active_tcp_offset_source": "operator_declaration_from_report",
        "active_tcp_offset_verified_on_pendant": cfg["robot"][
            "active_tcp_offset_verified_on_pendant"
        ],
        "calibration_status": cfg["mapping"]["calibration_status"],
    }
    writer = RunWriter(cfg["paths"]["runs"], metadata)
    print("Run directory:", writer.directory, flush=True)
    completed, last_sequence = 0, None
    start = last_success = time.monotonic()
    last_message = None
    limit = int(cfg["inference"]["max_predictions"]) if inference else 1
    try:
        with SensorSession(cfg) as sensors:
            metadata["mapping_origin_ur_base_m"] = sensors.mapping.origin_m.tolist()
            writer.metadata(metadata)
            while (
                completed < limit and time.monotonic() - start < cfg["inference"]["max_duration_s"]
            ):
                try:
                    observation, evidence = sensors.observation()
                except ValueError as exc:
                    reason = str(exc)
                    if reason != last_message:
                        writer.append({"event": "waiting_for_valid_observation", "reason": reason})
                        print(reason, flush=True)
                        last_message = reason
                    if time.monotonic() - last_success > cfg["observation"]["startup_timeout_s"]:
                        raise TimeoutError(
                            "no valid observation within configured timeout"
                        ) from exc
                    time.sleep(0.01)
                    continue
                if evidence["camera_sequences"][-1] == last_sequence:
                    time.sleep(0.005)
                    continue
                last_sequence = evidence["camera_sequences"][-1]
                last_message = None
                t0 = time.monotonic()
                record = {
                    "event": "prediction" if inference else "observation",
                    "index": completed,
                    "observation": evidence,
                    "agent_pos_px": observation["agent_pos"].tolist(),
                    "executed": False,
                }
                if inference:
                    inference_start = time.monotonic()
                    output = predict(policy, observation, synchronize_cuda=True)
                    validate_predictions(output, details["horizon"], details["n_action_steps"])
                    record.update(
                        {
                            "inference_s": time.monotonic() - inference_start,
                            "action_pred_px": output["action_pred"][0].tolist(),
                            "preview": preview_actions(output["action"][0], sensors.mapping),
                        }
                    )
                record["latest_image_host_age_at_completion_s"] = (
                    time.monotonic() - evidence["camera_host_monotonic_s"][-1]
                )
                if cfg["inference"]["save_observations"]:
                    writer.observation(completed, observation)
                writer.append(record)
                completed += 1
                last_success = time.monotonic()
                print(f"Recorded {completed}/{limit}; executed=False", flush=True)
                time.sleep(max(0, 1 / cfg["observation"]["rate_hz"] - (time.monotonic() - t0)))
            if completed != limit:
                raise TimeoutError(f"session ended after {completed}/{limit} records")
        writer.append({"event": "completed", "records": completed, "executed": False})
    except KeyboardInterrupt:
        writer.append({"event": "interrupted", "records": completed, "executed": False})
    except Exception as exc:
        writer.append(
            {
                "event": "failed",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "executed": False,
            }
        )
        raise
    finally:
        writer.close()
    return writer.directory


def prepare_candidate(
    output, mapping, guard, actual_pose, *, source_age_s, horizon, n_action_steps
):
    validate_predictions(output, horizon, n_action_steps)
    raw = output["action"][0, 0]
    desired = mapping.to_base(raw)
    target = guard.propose(desired, actual_pose, source_age_s=source_age_s)
    return {
        "raw_action_px": raw.tolist(),
        "desired_base_xyz_m": desired.tolist(),
        "target_pose_m_rad": target.tolist(),
        "source_age_s": source_age_s,
        "calibration_status": "engineering_mapping_not_calibrated",
        "gripper_action": "hold_no_command",
    }


def observation_source_stamp(evidence):
    effective = [
        stamp - max(0, delay)
        for stamp, delay in zip(
            evidence["camera_host_monotonic_s"], evidence["camera_ros_age_at_receive_s"]
        )
    ]
    return min(*effective, *evidence["robot_host_monotonic_s"])


@contextlib.contextmanager
def execution_lock(root):
    import fcntl

    path = root / ".runtime/guarded_execution.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def wait_observation(sensors, cfg, previous, deadline):
    last_error = None
    while time.monotonic() < deadline:
        try:
            obs, evidence = sensors.observation()
            if evidence["camera_sequences"][-1] != previous:
                return obs, evidence
        except ValueError as exc:
            last_error = exc
        time.sleep(0.01)
    raise TimeoutError("no new valid observation within bounded wait") from last_error


def run_execution(cfg, *, execute=False, site_ready=False):
    if execute and not site_ready:
        raise ValueError("live execution requires explicit site readiness")
    if execute and cfg["robot"].get("active_tcp_offset_verified_on_pendant") is not True:
        raise ValueError("confirmed active TCP is required for execution")
    for key in ["declared_active_tcp_offset_m_rad", "report_tcp_offset_m_rad"]:
        if not np.allclose(cfg["robot"][key], [0, 0, 0.244, 0, 0, 0], atol=1e-9, rtol=0):
            raise ValueError("this first-motion release requires the confirmed report TCP")
    if cfg["mapping"]["axes_in_ur_base"] != [[1, 0, 0], [0, 1, 0]]:
        raise ValueError("first-motion execution only supports UR base XY axes")
    limits = MotionLimits.visible()
    metadata = {
        "mode": "guarded_execute" if execute else "guarded_preview",
        "execution_enabled": execute,
        "operator_site_ready": site_ready,
        "gripper_control_enabled": False,
        "limits": asdict(limits),
        "platform_config": cfg,
        "environment": environment_versions(),
    }
    writer = RunWriter(cfg["paths"]["runs"], metadata)
    print("Run directory:", writer.directory, flush=True)
    completed = 0
    try:
        with execution_lock(cfg["_root"]):
            # CPU/CUDA initialization and first expensive prediction occur before control creation.
            import torch

            torch.manual_seed(int(cfg["inference"]["seed"]))
            policy, details = load_policy(cfg)
            metadata["model"] = details
            writer.metadata(metadata)
            with SensorSession(cfg) as sensors:
                start = time.monotonic()
                deadline = start + 60
                observation, evidence = wait_observation(sensors, cfg, None, start + 20)
                warmup = predict(policy, observation)
                validate_predictions(warmup, details["horizon"], details["n_action_steps"])
                previous = evidence["camera_sequences"][-1]
                writer.append({"event": "warmup_prediction_discarded", "executed": False})
                from rtde_receive import RTDEReceiveInterface

                receiver = RTDEReceiveInterface(
                    cfg["robot"]["ip"],
                    frequency=125.0,
                    variables=[
                        "timestamp",
                        "actual_TCP_pose",
                        "actual_q",
                        "actual_TCP_speed",
                        "actual_TCP_force",
                        "safety_mode",
                        "robot_mode",
                        "output_int_register_0",
                    ],
                )
                control = None
                executor = None
                try:
                    baseline = read_feedback(receiver)
                    guard = ActionGuard(baseline.pose, limits)

                    def reader():
                        return read_feedback(receiver)

                    monitor = GuardedRobot(None, reader, guard, baseline, emit=writer.append)
                    # Observe a stationary baseline before creating any control connection.
                    for _ in range(10):
                        state = reader()
                        monitor.check_feedback(state)
                        if np.linalg.norm(state.speed[:3]) > 0.0001:
                            raise ValueError("initial robot state is not stationary")
                        time.sleep(0.02)
                    metadata["initial_pose_m_rad"] = baseline.pose.tolist()
                    metadata["initial_q_rad"] = baseline.q.tolist()
                    metadata["initial_force"] = baseline.force.tolist()
                    metadata["mapping_origin_m"] = sensors.mapping.origin_m.tolist()
                    status = dashboard_status(cfg["robot"]["ip"])
                    metadata["dashboard_before"] = status
                    writer.metadata(metadata)
                    if execute:
                        require_dashboard_ready(status)
                        control = connect_control(cfg["robot"]["ip"], root=cfg["_root"])
                        executor = GuardedRobot(
                            control,
                            reader,
                            guard,
                            baseline,
                            emit=writer.append,
                            read_ready=control.guarded_ready,
                        )
                        writer.append({"event": "control_connected", "motion_sent": False})
                    for index in range(limits.max_commands):
                        observation, evidence = wait_observation(
                            sensors, cfg, previous, min(deadline, time.monotonic() + 10)
                        )
                        previous = evidence["camera_sequences"][-1]
                        t0 = time.monotonic()
                        output = predict(policy, observation)
                        inference_s = time.monotonic() - t0
                        state = reader()
                        (executor or monitor).check_feedback(state)
                        # Include ROS delay that preceded the bridge callback.
                        source_stamp = observation_source_stamp(evidence)
                        candidate = prepare_candidate(
                            output,
                            sensors.mapping,
                            guard,
                            state.pose,
                            source_age_s=time.monotonic() - source_stamp,
                            horizon=details["horizon"],
                            n_action_steps=details["n_action_steps"],
                        )
                        writer.observation(index, observation)
                        writer.append(
                            {
                                "event": "filtered_prediction",
                                "index": index,
                                "inference_s": inference_s,
                                "candidate": candidate,
                                "observation": evidence,
                                "action_px": output["action"][0].tolist(),
                                "action_pred_px": output["action_pred"][0].tolist(),
                                "actual_pose_m_rad": state.pose.tolist(),
                                "executed": False,
                            }
                        )
                        if execute:
                            target = np.asarray(candidate["target_pose_m_rad"])
                            if np.linalg.norm(target[:3] - state.pose[:3]) < 0.00001:
                                writer.append(
                                    {
                                        "event": "hold_below_deadband",
                                        "index": index,
                                        "executed": False,
                                    }
                                )
                            else:
                                executor.move(target, source_stamp_s=source_stamp)
                                completed += 1
                        print(
                            "FILTERED",
                            index + 1,
                            "live=",
                            execute,
                            "completed_moves=",
                            completed,
                            flush=True,
                        )
                        time.sleep(0.15)
                finally:
                    # Preserve an active failure while still attempting all owned cleanup.
                    import sys

                    active_error = sys.exc_info()[0] is not None
                    cleanup_error = None
                    try:
                        if executor is not None:
                            executor.close()
                        elif control is not None:
                            try:
                                control.stopScript()
                            finally:
                                control.disconnect()
                    except Exception as exc:
                        cleanup_error = exc
                        writer.append({"event": "control_cleanup_failed", "error": repr(exc)})
                    finally:
                        receiver.disconnect()
                    if cleanup_error is not None and not active_error:
                        raise cleanup_error
        writer.append(
            {
                "event": "completed",
                "motion_count": completed,
                "execution_enabled": execute,
                "gripper_control_enabled": False,
            }
        )
        return writer.directory
    except BaseException as exc:
        writer.append(
            {
                "event": "failed",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "motion_count": completed,
            }
        )
        raise
    finally:
        writer.close()
