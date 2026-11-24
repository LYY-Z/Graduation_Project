"""One-off migration of an explicitly isolated copy; not a runtime dependency."""
from pathlib import Path
import ast, hashlib, json, shutil, re

OLD=Path(r"G:\毕设\03_code\diffusion_policy_ur7e")
NEW=Path(r"G:\毕设\03_code\diffusion_policy_ur7e_refactored")
SRC=NEW/"src/dp_ur7e"
assert NEW.resolve()!=OLD.resolve() and NEW.name.endswith("_refactored")
def read(name): return (OLD/"src/dp_ur7e"/name).read_text(encoding="utf-8")
def write(path,text):
    path=Path(path)
    assert NEW.resolve() in path.resolve().parents
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text.rstrip()+"\n",encoding="utf-8")
def merged(doc,*parts):
    imports=[]; bodies=[]
    for text in parts:
        lines=text.splitlines(keepends=True)
        remove=set()
        tree=ast.parse(text)
        for index,node in enumerate(tree.body):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                remove.update(range(node.lineno-1,node.end_lineno))
                if isinstance(node,ast.ImportFrom) and node.module=="__future__": continue
                item="".join(lines[node.lineno-1:node.end_lineno]).strip()
                if item not in imports: imports.append(item)
            elif index==0 and isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                remove.update(range(node.lineno-1,node.end_lineno))
        bodies.append("".join(line for i,line in enumerate(lines) if i not in remove).strip())
    return '"""'+doc+'"""\n\nfrom __future__ import annotations\n\n'+"\n".join(imports)+"\n\n\n"+"\n\n\n".join(bodies)
def without_function(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    lines=text.splitlines(keepends=True)
    start=min([node.lineno]+[d.lineno for d in node.decorator_list])-1
    return "".join(lines[:start]+lines[node.end_lineno:])

# Keep historical and machine-specific materials local and outside public source.
legacy=NEW/".local/legacy"
legacy.mkdir(parents=True,exist_ok=True)
for name in ["artifacts","references","runs","configs"]:
    p=NEW/name
    if p.exists(): shutil.move(str(p),str(legacy/name))
for p in (OLD/"docs").iterdir():
    q=NEW/"docs"/p.name
    if q.exists():
        (legacy/"docs").mkdir(exist_ok=True)
        shutil.move(str(q),str(legacy/"docs"/p.name))
for name in ["requirements-adapter.txt","environment.inference.yml"]:
    p=NEW/name
    if p.exists(): shutil.move(str(p),str(legacy/name))
for name in ["cnn_config.yaml","pusht_image_transformer.download.json"]:
    p=NEW/"models"/name
    if p.exists():
        (legacy/"models").mkdir(exist_ok=True)
        shutil.move(str(p),str(legacy/"models"/name))
third=NEW/"third_party"
third.mkdir(exist_ok=True)
shutil.move(str(NEW/"upstream"),str(third/"diffusion_policy"))
sdk=third/"ur_rtde_guarded"
sdk.mkdir(exist_ok=True)
shutil.move(str(NEW/"vendor/ur_rtde_guarded"),str(sdk/"source"))
if not any((NEW/"vendor").iterdir()): (NEW/"vendor").rmdir()
shutil.copy2(OLD/"artifacts/control_backend.patch",sdk/"guarded.patch")
for part in ["hardware","inference","control"]:
    write(SRC/part/"__init__.py",'"""'+part.capitalize()+' interfaces for the UR7e deployment package."""')

# Image functions and atomic exchange keep their numerical implementations.
write(SRC/"hardware/camera.py",merged("RGB conversion and atomic frame exchange; independent of ROS and torch.",
    read("images.py"),read("frame_store.py")))
bridge=read("camera_bridge.py").replace("from .frame_store import CameraFrame, FrameStore","from .camera import CameraFrame, FrameStore").replace("from .images import decode_rgb_image, resize_for_policy","from .camera import decode_rgb_image, resize_for_policy")
write(SRC/"hardware/camera_bridge.py",bridge)
state=read("robot.py").replace("from .geometry import","from ..geometry import")
write(SRC/"hardware/robot_state.py",state)
history=read("observations.py").replace("from .frame_store import","from .camera import").replace("from .images import","from .camera import").replace("from .geometry import","from ..geometry import")
session=read("session.py").replace("from .frame_store import","from .camera import").replace("from .geometry import","from ..geometry import").replace("from .observations import ObservationHistory\n","").replace("from .robot import ReceiveOnlyRobot\n","")
session=session.replace("    def __enter__(self):\n        self.robot =", "    def __enter__(self):\n        from .robot_state import ReceiveOnlyRobot\n\n        self.robot =")
write(SRC/"hardware/observations.py",merged("Causal observation history and concurrent acquisition lifecycle.",history,session))

policy=read("model.py").replace('"""Strict official-checkpoint loading, invoked only by the manual shadow command."""','"""Verified upstream policy loading and a shared inference-only prediction wrapper."""')
predict_src=ast.get_source_segment(read("execution.py"),next(n for n in ast.parse(read("execution.py")).body if isinstance(n,ast.FunctionDef) and n.name=="predict"))
predict_src=predict_src.replace("def predict(policy, observation):","def predict(policy, observation, *, synchronize_cuda=False):\n    \"\"\"Predict original policy outputs without normalizing or clipping them twice.\n\n    Inputs are NumPy observation arrays; outputs retain upstream action units.\n    Optional CUDA synchronization supports comparable host-side timing.\n    \"\"\"")
predict_src=predict_src.replace("    with torch.inference_mode():","    if synchronize_cuda and policy.device.type == \"cuda\":\n        torch.cuda.synchronize(policy.device)\n    with torch.inference_mode():")
write(SRC/"inference/policy.py",policy+"\n\n"+predict_src)
write(SRC/"control/safety.py",read("motion_safety.py").replace("from .geometry import","from ..geometry import"))

# The critical GuardedRobot methods stay unchanged; only the loader/root plumbing moves.
motion=read("motion_robot.py").replace("from .geometry import","from ..geometry import").replace("from .motion_safety import","from .safety import")
motion=motion.replace("def connect_control(host):","def connect_control(host, *, root):")
motion=motion.replace("    from pathlib import Path\n\n    from .guarded_backend import load_backend\n\n    backend = load_backend(Path(__file__).resolve().parents[2])","    backend = load_backend(root)")
backend=read("guarded_backend.py").replace('"artifacts/control_backend.json"','".runtime/control_backend/manifest.json"').replace('"runtime/control_backend"','".runtime/control_backend"').replace('"vendor/ur_rtde_guarded"','"third_party/ur_rtde_guarded/source"')
backend=backend.replace('    for relative, expected in manifest["source_hashes"].items():','    hashes = manifest.get("source_hashes")\n    if not isinstance(hashes, dict) or not hashes:\n        raise ValueError("guarded backend source manifest is empty")\n    for relative, expected in hashes.items():')
backend=backend.replace('    spec = importlib.util.spec_from_file_location("dp_ur7e_rtde_control", binary)','    spec = importlib.util.spec_from_file_location("dp_ur7e_rtde_control", binary)\n    if spec is None or spec.loader is None:\n        raise ValueError("guarded backend is not a loadable extension")')
write(SRC/"control/robot.py",merged("Explicit guarded control boundary, private backend validation and feedback confirmation.",backend,motion))

runner=read("runner.py").replace("from .model import load_policy, validate_predictions","from .inference.policy import load_policy, predict, validate_predictions").replace("from .session import SensorSession","from .hardware.observations import SensorSession")
runner=runner.replace("def run(cfg, *, inference: bool):","def run_capture_shadow(cfg, *, inference: bool):")
start=runner.index("                if inference:\n                    import torch\n",runner.index("def run_capture_shadow"))
end=runner.index("                    record.update(",start)
runner=runner[:start]+"""                if inference:
                    inference_start = time.monotonic()
                    output = predict(policy, observation, synchronize_cuda=True)
                    validate_predictions(
                        output, details["horizon"], details["n_action_steps"]
                    )
"""+runner[end:]
execution=read("execution.py")
for name in ["main","predict"]: execution=without_function(execution,name)
execution=execution.replace('\nif __name__ == "__main__":\n    main()\n',"")
execution=execution.replace("import argparse\n","").replace("import signal\n","").replace("from pathlib import Path\n","").replace("from .config import load_config\n","")
execution=execution.replace("from .model import load_policy, validate_predictions","from .inference.policy import load_policy, predict, validate_predictions").replace("from .motion_robot import","from .control.robot import").replace("from .motion_safety import","from .control.safety import").replace("from .session import SensorSession","from .hardware.observations import SensorSession")
execution=execution.replace('"runtime/guarded_execution.lock"','".runtime/guarded_execution.lock"').replace("path.parent.mkdir(exist_ok=True)","path.parent.mkdir(parents=True, exist_ok=True)")
execution=execution.replace('connect_control(cfg["robot"]["ip"])','connect_control(cfg["robot"]["ip"], root=cfg["_root"])')
write(SRC/"pipeline.py",merged("Explicit capture, shadow, preview and guarded execution workflows.",runner,execution))
for name in ["camera_bridge.py","images.py","frame_store.py","robot.py","session.py","observations.py","model.py","runner.py","execution.py","motion_safety.py","motion_robot.py","guarded_backend.py"]:
    (SRC/name).unlink()

# Migrate the existing regression suite without weakening assertions.
replacements={
"dp_ur7e.camera_bridge":"dp_ur7e.hardware.camera_bridge",
"dp_ur7e.images":"dp_ur7e.hardware.camera",
"dp_ur7e.frame_store":"dp_ur7e.hardware.camera",
"dp_ur7e.observations":"dp_ur7e.hardware.observations",
"dp_ur7e.session":"dp_ur7e.hardware.observations",
"dp_ur7e.robot":"dp_ur7e.hardware.robot_state",
"dp_ur7e.model":"dp_ur7e.inference.policy",
"dp_ur7e.runner":"dp_ur7e.pipeline",
"dp_ur7e.motion_robot":"dp_ur7e.control.robot",
"dp_ur7e.motion_safety":"dp_ur7e.control.safety",
"dp_ur7e.guarded_backend":"dp_ur7e.control.robot",
"from dp_ur7e import motion_safety":"from dp_ur7e.control import safety as motion_safety",
"from dp_ur7e import motion_robot":"from dp_ur7e.control import robot as motion_robot",
"from dp_ur7e import execution":"from dp_ur7e import pipeline as execution",
'"configs/platform.yaml"':'"config.example.yaml"',
'root / "upstream"':'root / "third_party/diffusion_policy"',
'(tmp_path / "artifacts").mkdir()':'(tmp_path / ".runtime/control_backend").mkdir(parents=True)',
'"artifacts/control_backend.json"':'".runtime/control_backend/manifest.json"',
}
for path in (NEW/"tests").glob("test_*.py"):
    if path.name=="test_public_interface.py":continue
    text=path.read_text(encoding="utf-8")
    for a,b in replacements.items():text=text.replace(a,b)
    write(path,text)
print("Source modules grouped; existing tests migrated without changing their assertions.")

