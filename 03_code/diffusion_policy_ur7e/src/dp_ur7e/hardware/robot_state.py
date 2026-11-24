"""Explicit RTDE receive-only access. No RTDE control or script upload."""

from __future__ import annotations

import time

from ..geometry import finite_vector, report_tcp_position
from .observations import RobotSample


class ReceiveOnlyRobot:
    def __init__(self, receiver, active_offset, report_offset):
        self.receiver = receiver
        self.active_offset = finite_vector(active_offset, 6, "declared active TCP offset")
        self.report_offset = finite_vector(report_offset, 6, "report TCP offset")

    @classmethod
    def connect(cls, robot_cfg):
        # This import and connection occur only in explicit manual capture/shadow commands.
        from rtde_receive import RTDEReceiveInterface

        receiver = RTDEReceiveInterface(
            robot_cfg["ip"],
            frequency=float(robot_cfg["receive_hz"]),
            variables=[
                "timestamp",
                "actual_TCP_pose",
                "actual_q",
                "safety_mode",
                "robot_mode",
            ],
        )
        return cls(
            receiver,
            robot_cfg["declared_active_tcp_offset_m_rad"],
            robot_cfg["report_tcp_offset_m_rad"],
        )

    def read(self) -> RobotSample:
        # Getters share a background-updated state. Retry if a packet changes mid-read.
        for _ in range(5):
            before = float(self.receiver.getTimestamp())
            pose = finite_vector(self.receiver.getActualTCPPose(), 6, "actual TCP pose")
            q = finite_vector(self.receiver.getActualQ(), 6, "joint positions")
            safety, mode = (
                int(self.receiver.getSafetyMode()),
                int(self.receiver.getRobotMode()),
            )
            after = float(self.receiver.getTimestamp())
            if before == after:
                result = RobotSample(
                    time.monotonic(),
                    after,
                    report_tcp_position(pose, self.active_offset, self.report_offset),
                    pose,
                    q,
                    safety,
                    mode,
                )
                result.validate()
                return result
        raise RuntimeError("RTDE packet changed during every read attempt")

    def close(self):
        self.receiver.disconnect()
