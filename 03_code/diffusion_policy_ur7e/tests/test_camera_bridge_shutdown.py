"""Lifecycle regressions using real ROS contexts, without a camera or robot.

The ordinary non-ROS test suite skips these cases. On the server run with
ROS system Python: python3 -m unittest discover -s tests -p test_camera_bridge_shutdown.py -v
Only spin_once is replaced to inject stop/error events deterministically;
the bridge, node, subscription and ROS context lifecycle remain real.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import rclpy
except ImportError:
    rclpy = None

from dp_ur7e.hardware.camera_bridge import run_camera_bridge


@unittest.skipIf(rclpy is None, "requires ROS system Python and rclpy")
class CameraBridgeShutdownTests(unittest.TestCase):
    def setUp(self):
        temp_root = Path(__file__).resolve().parents[1] / "runs" / "test_tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(dir=temp_root)
        self.contexts = []
        self.cfg = {
            "paths": {"frame_store": Path(self.directory.name) / "rgb.npz"},
            "camera": {
                "topic": f"/dp_ur7e_lifecycle_test_{os.getpid()}/rgb",
                "expected_frame_id": "test_color_optical_frame",
                "publication_hz": 30.0,
                "image_shape_hw": [96, 96],
                "roi_xywh": None,
            },
            "observation": {"max_age_s": 0.5},
        }

    def tearDown(self):
        rclpy.try_shutdown()
        self.directory.cleanup()

    def run_with_event(self, event):
        def spin_once(node, *, timeout_sec):
            self.contexts.append(node.context)
            event(node)

        with patch.object(rclpy, "spin_once", side_effect=spin_once):
            run_camera_bridge(self.cfg)

    def assert_contexts_closed(self):
        self.assertTrue(self.contexts)
        self.assertTrue(all(not context.ok() for context in self.contexts))

    def test_interrupt_after_ros_shutdown_returns_without_cleanup_error(self):
        def interrupt(node):
            node.context.try_shutdown()
            raise KeyboardInterrupt

        self.run_with_event(interrupt)
        self.assert_contexts_closed()

    def test_ros_context_stop_without_keyboard_interrupt_returns_normally(self):
        self.run_with_event(lambda node: node.context.try_shutdown())
        self.assert_contexts_closed()

    def test_keyboard_interrupt_with_active_context_still_closes_context(self):
        def interrupt(node):
            raise KeyboardInterrupt

        self.run_with_event(interrupt)
        self.assert_contexts_closed()

    def test_rejected_sample_error_is_not_masked_by_repeated_shutdown(self):
        failure = ValueError("invalid camera sample")

        def reject(node):
            node.failure = failure
            node.context.try_shutdown()

        with self.assertRaisesRegex(RuntimeError, "camera bridge rejected") as caught:
            self.run_with_event(reject)
        self.assertIs(caught.exception.__cause__, failure)
        self.assert_contexts_closed()

    def test_unexpected_executor_error_still_propagates_and_closes_context(self):
        failure = OSError("executor transport failure")

        def fail(node):
            raise failure

        with self.assertRaises(OSError) as caught:
            self.run_with_event(fail)
        self.assertIs(caught.exception, failure)
        self.assert_contexts_closed()
