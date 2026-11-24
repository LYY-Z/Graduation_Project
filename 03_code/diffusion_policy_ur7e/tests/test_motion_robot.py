"""Instrumented hardware boundary, not an imitation of the numerical guards."""

from dataclasses import replace

import numpy as np
import pytest

from dp_ur7e.control.safety import ActionGuard


def api():
    try:
        from dp_ur7e.control import robot as motion_robot
    except ImportError:
        pytest.fail("guarded execution boundary has not been implemented")
    return motion_robot


class Clock:
    now = 10.0

    def __call__(self):
        return self.now

    def sleep(self, duration):
        self.now += duration


class Hardware:
    def __init__(self):
        self.pose = [0.3, -0.2, 0.4, 0, 3.14, 0]
        self.q = np.zeros(6)
        self.target = None
        self.calls = []
        self.pose_safe = self.joints_safe = self.accept = True
        self.ik_delta = 0.0
        self.offset = [0, 0, 0.244, 0, 0, 0]
        self.complete = True

    def getTCPOffset(self):
        return self.offset

    def isPoseWithinSafetyLimits(self, pose):
        return self.pose_safe

    def isJointsWithinSafetyLimits(self, q):
        return self.joints_safe

    def getInverseKinematics(self, pose, near):
        return np.asarray(near) + self.ik_delta

    def getAsyncOperationProgress(self):
        return (
            -2 if self.target is not None and self.complete else (-1 if self.target is None else 0)
        )

    def moveL(self, pose, speed, acceleration, asynchronous):
        self.calls.append(("moveL", pose, speed, acceleration, asynchronous))
        self.target = pose
        if self.complete:
            self.pose = list(pose)
        return self.accept

    def stopL(self, acceleration):
        self.calls.append(("stopL", acceleration))

    def stopScript(self):
        self.calls.append(("stopScript",))

    def disconnect(self):
        self.calls.append(("disconnect",))


def setup():
    mod = api()
    hw = Hardware()
    clock = Clock()

    def read():
        return mod.Feedback(
            clock(),
            clock(),
            np.array(hw.pose),
            np.array(hw.q),
            np.zeros(6),
            np.zeros(6),
            1,
            7,
        )

    initial = read()
    g = ActionGuard(initial.pose)
    executor = mod.GuardedRobot(
        hw, read, g, initial, clock=clock, sleep=clock.sleep, read_ready=lambda: 1
    )
    return executor, hw, clock, g, initial


def test_move_uses_only_bounded_target_and_explicit_slow_parameters():
    e, h, c, g, _ = setup()
    target = g.propose([2, 2, 2], h.pose, source_age_s=0.5)
    result = e.move(target, source_stamp_s=c() - 0.5)
    motion = [x for x in h.calls if x[0] == "moveL"]
    assert len(motion) == 1
    assert motion[0][2:] == (0.001, 0.005, True)
    np.testing.assert_array_equal(motion[0][1], target)
    np.testing.assert_allclose(result["actual_after"], target)
    assert result["completed"] is True


def test_waits_for_stable_ready_before_final_fresh_checks():
    e, h, c, g, _ = setup()
    started = c()
    e.read_ready = lambda: 2 if c() - started < 0.03 else 1
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    result = e.move(target, source_stamp_s=c() - 0.5)
    assert result["completed"]
    assert c() - started >= 0.05


def test_never_sends_if_control_script_does_not_become_ready():
    e, h, c, g, _ = setup()
    e.read_ready = lambda: 2
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    with pytest.raises(TimeoutError, match="ready"):
        e.move(target, source_stamp_s=c() - 0.5)
    assert not any(x[0] == "moveL" for x in h.calls)


@pytest.mark.parametrize("problem", ["pose", "joints", "ik", "oversize", "stale", "tcp"])
def test_rejections_never_send_a_move(problem):
    e, h, c, g, _ = setup()
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    stamp = c() - 0.5
    if problem == "pose":
        h.pose_safe = False
    if problem == "joints":
        h.joints_safe = False
    if problem == "ik":
        h.ik_delta = 0.1
    if problem == "oversize":
        target[0] += 0.01
    if problem == "stale":
        stamp = c() - 2
    if problem == "tcp":
        h.offset = [0] * 6
    with pytest.raises((ValueError, RuntimeError)):
        e.move(target, source_stamp_s=stamp)
    assert not any(x[0] == "moveL" for x in h.calls)


def test_motion_timeout_stops_and_does_not_retry():
    e, h, c, g, _ = setup()
    h.complete = False
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    with pytest.raises(TimeoutError):
        e.move(target, source_stamp_s=c() - 0.5)
    assert sum(x[0] == "moveL" for x in h.calls) == 1
    assert any(x[0] == "stopL" for x in h.calls)


def test_zero_measured_travel_cannot_be_reported_as_completed():
    e, h, c, g, _ = setup()
    original = h.moveL
    pose = list(h.pose)

    def acknowledged_without_travel(*args):
        result = original(*args)
        h.pose = pose
        return result

    h.moveL = acknowledged_without_travel
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    with pytest.raises(TimeoutError):
        e.move(target, source_stamp_s=c() - 0.5)
    assert any(x[0] == "stopL" for x in h.calls)


def test_stationarity_rechecked_after_controller_queries():
    e, h, c, g, initial = setup()
    reads = 0

    def read():
        nonlocal reads
        reads += 1
        return replace(
            initial,
            host_s=c(),
            controller_s=c(),
            speed=np.array([0.0005 if reads > 1 else 0, 0, 0, 0, 0, 0]),
        )

    e.read = read
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    with pytest.raises(ValueError, match="stationary"):
        e.move(target, source_stamp_s=c() - 0.5)
    assert not any(x[0] == "moveL" for x in h.calls)


def test_slow_intent_log_cannot_cause_stale_dispatch():
    e, h, c, g, _ = setup()
    e.emit = lambda event: c.sleep(2) if event["event"] == "motion_dispatch_intent" else None
    target = g.propose([1, 1, 1], h.pose, source_age_s=0.5)
    with pytest.raises(ValueError, match="stale"):
        e.move(target, source_stamp_s=c() - 0.5)
    assert not any(x[0] == "moveL" for x in h.calls)


def test_false_move_acknowledgement_stops():
    e, h, c, g, _ = setup()
    h.accept = False
    with pytest.raises(RuntimeError):
        e.move(g.propose([1, 1, 1], h.pose, source_age_s=0.5), source_stamp_s=c() - 0.5)
    assert any(x[0] == "stopL" for x in h.calls)


def test_ctrl_c_during_motion_stops_before_propagating():
    e, h, c, g, _ = setup()

    def interrupted():
        raise KeyboardInterrupt()

    # Source is checked before sending; interrupt the monitor after motion dispatch.
    original = e.read

    def read():
        if h.target is not None:
            interrupted()
        return original()

    e.read = read
    with pytest.raises(KeyboardInterrupt):
        e.move(g.propose([1, 1, 1], h.pose, source_age_s=0.5), source_stamp_s=c() - 0.5)
    assert any(x[0] == "stopL" for x in h.calls)


@pytest.mark.parametrize(
    "field,value",
    [
        ("safety_mode", 3),
        ("robot_mode", 5),
        ("host_s", 8.0),
        ("speed", np.array([0.003, 0, 0, 0, 0, 0])),
        ("q", np.ones(6) * 0.1),
        ("force", np.array([6, 0, 0, 0, 0, 0])),
        ("pose", np.array([0.4, -0.2, 0.4, 0, 3.14, 0])),
    ],
)
def test_bad_feedback_is_rejected(field, value):
    e, h, c, g, initial = setup()
    with pytest.raises(ValueError):
        e.check_feedback(replace(initial, **{field: value}))


def test_controller_timestamp_stall_is_detected():
    e, h, c, g, initial = setup()
    e.check_feedback(initial)
    c.sleep(0.25)
    with pytest.raises(ValueError, match="timestamp"):
        e.check_feedback(replace(initial, host_s=c()))


def test_cleanup_stops_script_and_disconnects():
    e, h, *_ = setup()
    e.close()
    assert [x[0] for x in h.calls] == ["stopL", "stopScript", "disconnect"]
    assert h.calls[0][1] == 0.005


def test_cleanup_retains_failure_and_still_disconnects():
    e, h, *_ = setup()

    def fail(a):
        raise OSError("link failed")

    h.stopL = fail
    with pytest.raises(OSError, match="link failed"):
        e.close()
    assert [x[0] for x in h.calls] == ["stopScript", "disconnect"]
