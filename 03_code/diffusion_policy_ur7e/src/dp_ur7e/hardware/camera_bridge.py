"""Manual ROS 2 RGB subscriber. No camera-driver or robot startup side effects."""

from __future__ import annotations

import time
import uuid

from .camera import CameraFrame, FrameStore
from .camera import decode_rgb_image, resize_for_policy


def run_camera_bridge(cfg):
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import qos_profile_sensor_data
    from sensor_msgs.msg import Image

    camera_cfg = cfg["camera"]
    store = FrameStore(cfg["paths"]["frame_store"])
    stream_id = uuid.uuid4().hex
    rclpy.init(args=[])

    class CameraBridge(Node):
        def __init__(self):
            super().__init__("dp_ur7e_wrist_rgb_bridge")
            self.sequence = 0
            self.last_ros_stamp = None
            self.last_write = -float("inf")
            self.failure = None
            self.subscription = self.create_subscription(
                Image, camera_cfg["topic"], self.receive, qos_profile_sensor_data
            )
            self.get_logger().info(
                f"RGB topic={camera_cfg['topic']}; output={store.path}; stream={stream_id}"
            )

        def receive(self, message):
            receipt = time.monotonic()
            if receipt - self.last_write < 1 / camera_cfg["publication_hz"]:
                return
            try:
                if message.header.frame_id != camera_cfg["expected_frame_id"]:
                    raise ValueError("unexpected optical frame: " + message.header.frame_id)
                stamp = message.header.stamp.sec + message.header.stamp.nanosec / 1e9
                age = self.get_clock().now().nanoseconds / 1e9 - stamp
                if age < -0.05 or age > cfg["observation"]["max_age_s"]:
                    raise ValueError(
                        f"ROS image timestamp is stale or future-dated: age={age:.6f}s"
                    )
                if self.last_ros_stamp is not None and stamp <= self.last_ros_stamp:
                    raise ValueError("camera header timestamp did not advance")
                rgb = decode_rgb_image(message)
                resized = resize_for_policy(
                    rgb, camera_cfg["image_shape_hw"], camera_cfg["roi_xywh"]
                )
                frame = CameraFrame(
                    resized,
                    self.sequence,
                    receipt,
                    stamp,
                    message.header.frame_id,
                    stream_id,
                    tuple(rgb.shape[:2]),
                    message.encoding,
                    age,
                )
                store.write(frame)
                self.sequence += 1
                self.last_ros_stamp = stamp
                self.last_write = receipt
            except Exception as exc:
                self.failure = exc

    node = CameraBridge()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.25)
            if node.failure is not None:
                raise RuntimeError("camera bridge rejected an incoming sample") from node.failure
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # SIGINT may have already shut down the default ROS context.
        rclpy.try_shutdown()
