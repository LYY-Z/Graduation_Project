# UR7e Diffusion Policy Deployment Guide

[English](guide.md) | [简体中文](guide.CN.md)

This guide covers runtime environments, model resources, device configuration, and process entry points. Implementation and control limits are documented in the [technical report](technical_report.md); validation scope and record provenance are listed in the [validation data](validation.json).

Deployment produces the inference environment, model file, and control extension. Runtime processes comprise the camera driver, image bridge, and policy application. All commands below run from the repository root on a Linux host.

## 1. Runtime environments

| Environment | Purpose | Dependencies |
|---|---|---|
| Inference environment | Policy application, model and resource checks, control-extension build | Conda; project environment `.envs/inference`, Python 3.9 |
| ROS environment | Camera driver and image bridge | Ubuntu 22.04, ROS 2 Humble, system Python 3.10, `orbbec_camera` |
| Native build tools | Compile the project-specific control extension | CMake, G++, Boost |
| Compute device | Model inference | NVIDIA GPU and compatible driver; CUDA runtime 11.6 in the environment |

### 1.1 Environment setup

`scripts/prepare_environment.sh` creates the inference environment from `environment.yml`, registers project sources, and checks dependencies. An existing environment enters the installation and verification stages. Reports are written to `runs/validation/environment/`.

```bash
bash scripts/prepare_environment.sh
```

Checks cover dependency imports, CUDA availability, and protected-environment metadata consistency, without model initialization or device access. `--verify-only` checks an existing environment.

### 1.2 Application terminal

Application commands use the interpreter in `.envs/inference`. Initialize the terminal with:

```bash
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
export PYTHONNOUSERSITE=1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ./.envs/inference
```

Clearing these environment variables isolates ROS and inference dependencies. The ROS driver and bridge run in separate terminals with the setup in Section 4. Conda activation selects the interpreter; the repository directory does not select it.

## 2. Model and control resources

### 2.1 Model acquisition and integrity checks

The current model is the official simulated Push-T image Transformer checkpoint. `models/checkpoint_manifest.json` fixes the download URL, file size, and SHA-256. The downloaded file is stored at `models/pusht_image_transformer.ckpt`.

```bash
python scripts/fetch_checkpoint.py
python scripts/verify_bundle.py --check-model
```

The two operations have distinct inputs and results:

| Tool | Input and verification target | Success result |
|---|---|---|
| `fetch_checkpoint.py` | Model manifest and official weights | Size and SHA-256 match; outputs `verified: true`; an existing valid file is verified and reused |
| `verify_bundle.py --check-model` | Locked upstream sources, ur_rtde sources and patch, checkpoint | Outputs source-file counts, `patch_verified: true`, and `checkpoint_verified: true` |

The locked source baseline contains 369 policy files and 339 SDK files. Resource verification does not deserialize the model, initialize CUDA, or access devices. Runtime modes trigger model loading.

`models/transformer_config.yaml` is a model-configuration reference. The embedded checkpoint configuration constructs the network; saved model parameters supply EMA weights and normalization state. `config.yaml` supplies hardware, path, and session settings.

### 2.2 Control-extension build

`execute` uses the project-specific `dp_ur7e_rtde_control` extension. The build script takes `third_party/ur_rtde_guarded/` as input and produces `.runtime/control_backend/manifest.json` after compilation, native loopback tests, and module-coexistence checks.

```bash
python scripts/build_backend.py --jobs 2
```

The extension binds to the inference environment's Python ABI and is compiled on the deployment host. `--plan` displays the build commands. Build tests do not connect to the robot. The active manifest records source and binary hashes; a failed candidate build leaves the active version intact.

State acquisition uses the installed `rtde_receive` module; motion execution loads the private Control module. Loading rules and control patches are described in the [technical report](technical_report.md#4-action-execution).

## 3. Device and runtime configuration

Create the local configuration from the [template](../config.example.yaml):

```bash
cp -n config.example.yaml config.yaml
```

`config.yaml` uses schema 2. `project_root` resolves relative to the configuration file; other project paths resolve relative to `project_root`. Deployment settings cover the following interfaces:

| Configuration group | Settings to verify |
|---|---|
| `paths` | Upstream sources, weights, image exchange file, and run records |
| `robot` | Controller address, acquisition rate, coordinate frame, and active TCP |
| `camera` | Image topic, `frame_id`, crop region, and bridge rate |
| `observation` | Window length, sampling grid, freshness, and pairing limits |
| `mapping` | Mapping between virtual action coordinates and the UR base frame |
| `inference`, `execution` | Device, seed, recording scope, and execution backend |

The template address `192.0.2.1` is a documentation placeholder accepted only by `inspect`. Hardware modes require the actual controller address. Camera model and serial fields are descriptive; the external driver's launch arguments select the device.

The current interface uses two `96×96` RGB observations and two-dimensional positions. The tool TCP is `[0,0,0.244,0,0,0]` in metres and rotation-vector radians. Execution checks both the configuration declaration and the controller's active TCP. The engineering mapping of virtual action coordinates does not include camera calibration.

The complete field reference is in [Appendix B](#appendix-b-configuration-fields). Model interfaces, coordinate transforms, and numerical limits are documented in the [technical report](technical_report.md).

## 4. Runtime interfaces

### 4.1 Processes and data flow

The camera driver publishes RGB messages; the bridge converts images into local NPZ data; the policy application reads images and acquires robot state through RTDE. The application initializes the model, manages acquisition threads, and coordinates the selected mode.

| Process | Environment and entry point | Output |
|---|---|---|
| Camera driver | ROS environment; [camera configuration](#appendix-a-camera-configuration) | `/wrist_camera/color/image_raw` |
| Image bridge | ROS environment; `camera-bridge` | Image exchange file specified by `paths.frame_store` |
| Policy application | Inference environment; `inspect / capture / shadow / preview / execute` | Run records; `execute` also sends motion commands |

The bridge and application run on the same host. The application establishes RTDE interfaces directly, without a ROS robot driver. An image-stream restart requires a new application session.

### 4.2 Image bridge

Load the ROS environment and start the bridge in a ROS terminal. A source-installed camera driver additionally requires its workspace environment.

```bash
source /opt/ros/humble/setup.bash
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD/src:$PYTHONPATH"

/usr/bin/python3 -m dp_ur7e camera-bridge --config config.yaml
```

The bridge validates the message type, image encoding, and `frame_id`, then writes the configured image exchange file. The policy application builds observation windows from that file.

### 4.3 Policy application

Select a CLI mode in the inference environment from Section 1.2:

| Mode | Processing scope | Motion control |
|---|---|---|
| `inspect` | Configuration, resource paths, and model-file verification | No device connections |
| `capture` | Acquire and save one real observation window | Receive only |
| `shadow` | Real observation acquisition, policy inference, and recording | Receive only |
| `preview` | Inference, action mapping, filtering, and target preview | Receive only, with controller-status queries |
| `execute` | Inference, target checks, motion execution, and feedback verification | Receive and private Control |

Shadow-inference entry point:

```bash
python -m dp_ur7e shadow --config config.yaml
```

Execution requires Remote Control, normal safety mode, an idle program state, a stationary arm, and verified active TCP and motion clearance. `--site-ready` explicitly declares these site conditions for the invocation:

```bash
python -m dp_ur7e execute --config config.yaml --site-ready
```

`preview` and `execute` perform warmup, then process at most three candidate targets. Execution applies limits, smoothing, controller checks, and feedback verification. Full control constraints are listed in the [technical report](technical_report.md#4-action-execution). Diagnostic modes and execution are independent entry points.

Application exit releases its own threads and connections; the external driver and bridge retain independent lifecycles. Motion commands are not retried automatically, and the program does not return the arm to its initial pose.

## 5. Run records and validation

Each application session reports a directory under `runs/<UTC>_<short-id>/`:

| File | Contents |
|---|---|
| `metadata.json` | Mode, configuration, environment, and model provenance |
| `events.jsonl` | Observations, predictions, filtering, command acknowledgements, measured feedback, and termination state |
| `observations/*.npz` | Policy input windows; capture/shadow use the recording option |

`summarize_run.py` reads the selected directory's event file and reports command acknowledgements, completed motions, and position metrics. Distances are in metres. `RUN_ID` is the actual session-directory name reported by the application:

```bash
python scripts/summarize_run.py runs/RUN_ID
```

Session completion, command acknowledgement, and measured arrival are counted separately. Motion evidence comprises `motion_command_acknowledged`, feedback, and `motion` events with `completed=true`. `filtered_prediction.executed=false` describes the candidate at creation; subsequent execution is recorded separately. Task success is a separate evaluation metric.

### Minimal shadow-inference validation example

Inputs are a valid device configuration, an advancing RGB stream, and RTDE state. Set `inference.max_predictions=1` and `inference.save_observations=true`, then run `shadow` to validate one observation–prediction–recording cycle.

On normal completion, the terminal reports `Recorded 1/1; executed=False` and produces:

| Data | Expected structure |
|---|---|
| `observations/000000.npz` | `image: [1,2,3,96,96]` and `agent_pos: [1,2,2]`, both float32 |
| `prediction` event | `action_pred_px: [10,2]` and `preview.raw_action_px: [8,2]`; event storage removes the batch dimension |
| Run summary | `run_completed: true`; `acknowledged_motions`, `completed_motions`, and `feedback_samples` are all 0 |

The structures match the archived shadow record indexed under `non_motion_example` in the [validation data](validation.json). This check covers data interfaces and inference outputs; task performance and hardware regression for the current version are assessed separately.

## 6. Development checks and troubleshooting

Development checks use a separate Python 3.11 environment with dependencies from the `dev` group in `pyproject.toml`:

```bash
conda create --prefix .envs/dev python=3.11 pip --yes
conda activate ./.envs/dev
python -m pip install -e ".[dev]"
```

Offline tests and static checks:

```bash
python -m pytest -q
python -m ruff check src tests scripts
```

Offline tests substitute model and hardware boundaries; ROS lifecycle cases run in a ROS environment. Hardware acceptance scope is recorded in the [validation data](validation.json).

| Failure area | Inspection targets |
|---|---|
| Module imports | `sys.executable`, `sys.prefix`, and registered source location |
| Images and observation windows | Driver topic, `frame_id`, exchange-file path, timestamps, and RTDE updates |
| Model or extension verification | Provenance manifests, file hashes, Python ABI, and local build results |
| Target rejection or timeout | Observation age, inference latency, workspace limits, and controller state |
| Stop or cleanup error | Actual robot state, platform stop procedure, and error records; logs do not establish a confirmed stop |

## Appendix A. Camera configuration

The single wrist camera uses the RGB configuration below. `CAMERA_SERIAL` selects the target device:

```bash
source /opt/ros/humble/setup.bash
CAMERA_SERIAL="YOUR_WRIST_CAMERA_SERIAL"

ros2 launch orbbec_camera gemini_330_series.launch.py \
  camera_name:=wrist_camera "serial_number:=$CAMERA_SERIAL" device_num:=1 \
  enable_color:=true color_format:=MJPG \
  color_width:=640 color_height:=480 color_fps:=30 \
  enable_depth:=false enable_left_ir:=false enable_right_ir:=false \
  enable_point_cloud:=false enable_colored_point_cloud:=false \
  enable_accel:=false enable_gyro:=false \
  publish_tf:=false enumerate_net_device:=false
```

| Component | Recorded configuration |
|---|---|
| UR7e controller | CB5 v5.5; PolyScope 5.23.0 (platform report) |
| Tool TCP | `[0,0,244]` mm, zero rotation |
| Wrist camera | Gemini 335L; firmware 1.4.60; SDK 2.7.6 |
| ROS driver | `orbbec_camera`, `gemini_330_series.launch.py` |
| Color stream | 640×480, requested 30 fps, MJPG device transport |

Record provenance is indexed under `hardware_reference` in the [validation data](validation.json); the exact ROS Wrapper version was not recorded. Inspect driver metadata for the installed version and supported arguments:

```bash
ros2 pkg xml orbbec_camera --tag version
ros2 launch orbbec_camera gemini_330_series.launch.py --show-args
```

The image interface requires `sensor_msgs/msg/Image`, `rgb8` or `bgr8` encoding, frame `wrist_camera_color_optical_frame`, and advancing timestamps. Topic inspection commands:

```bash
ros2 topic info /wrist_camera/color/image_raw --verbose
ros2 topic echo /wrist_camera/color/image_raw --once --field header \
  --qos-reliability best_effort
```

The 30 fps setting is a requested acquisition rate; actual observation and inference rates depend on data arrival and processing latency. Argument definitions are provided in the [official launch file](https://github.com/orbbec/OrbbecSDK_ROS2/blob/v2-main/orbbec_camera/launch/gemini_330_series.launch.py).

## Appendix B. Configuration fields

| Fields | Purpose |
|---|---|
| `schema_version`, `project_root` | Configuration version `2`; the configuration-file directory is the project-root base |
| `paths.upstream` | Fixed official policy source directory |
| `paths.checkpoint`, `paths.checkpoint_manifest`, `paths.official_config` | Weights, model manifest, readable model configuration |
| `paths.frame_store`, `paths.runs` | Image exchange file and run-record directory |
| `robot.model`, `camera.model`, `camera.serial` | Hardware description; the external driver selects the camera |
| `robot.ip` | Controller IP |
| `robot.state_interface`, `robot.receive_hz` | `rtde_receive_only`; requested acquisition rate, default 125 Hz |
| `robot.pose_frame` | `ur_base` frame declaration; the adapter computes coordinate transforms |
| `robot.declared_active_tcp_offset_m_rad` | Declared active TCP offset in metres and rotation-vector radians |
| `robot.report_tcp_offset_m_rad` | Report TCP offset, currently `[0,0,0.244,0,0,0]` |
| `robot.active_tcp_offset_verified_on_pendant` | Set `true` after checking the active TCP on the pendant; required by execution |
| `camera.topic`, `camera.expected_frame_id` | RGB topic and optical frame; both must match the driver |
| `camera.image_shape_hw`, `camera.roi_xywh` | Fixed output `[96,96]`; ROI uses source pixels `[x,y,width,height]`, with `null` selecting a centre-square crop |
| `camera.publication_hz`, `camera.frame_store_poll_hz` | Bridge write ceiling 30 Hz; file polling 100 Hz, without changing camera exposure rate |
| `observation.n_obs_steps`, `observation.rate_hz` | Two observations on a nominal 10 Hz time grid |
| `observation.max_age_s`, `observation.max_acquisition_skew_s` | Sample age limit 0.5 s; camera/state pairing skew limit 0.05 s |
| `observation.startup_timeout_s` | Capture/shadow invalid-observation retry timeout, default 20 s |
| `mapping.mode`, `mapping.calibration_status` | `relative_anchor`, labelled `engineering_mapping_not_calibrated` |
| `mapping.anchor_px`, `mapping.pixels_per_m` | Initial virtual coordinate `[256,256]`; scale `[1000,1000]` virtual pixels/metre |
| `mapping.axes_in_ur_base`, `mapping.model_bounds_px` | Base XY axes; virtual-coordinate range `[0,512]` |
| `inference.device`, `inference.seed` | Compute device, default `cuda:0`; random seed 42 |
| `inference.max_predictions`, `inference.max_duration_s` | Shadow target count 20; capture/shadow duration limit 120 s |
| `inference.save_observations` | Save capture/shadow input windows, default `true` |
| `execution.implementation`, `execution.default_mode` | Fixed as `guarded` and `preview`; execution is explicitly selected by the CLI mode |

`preview` / `execute` use separate session bounds: 20 s for the initial observation, 10 s for later observations, a 60 s observation-loop deadline, and at most three candidates. These bounds are independent of `inference.max_predictions` and `inference.max_duration_s`. Startup, warmup, controller queries, and cleanup have their own processing time; 60 s is not a hard real-time bound on the entire process. Preview/execute always save input windows.
