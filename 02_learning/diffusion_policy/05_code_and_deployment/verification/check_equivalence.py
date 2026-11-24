"""Offline structural and numerical comparison with the preserved source release."""
from pathlib import Path
import ast
import importlib.util
import json
import sys
from types import SimpleNamespace
import numpy as np

sys.dont_write_bytecode=True
OLD=Path(r"G:\毕设\03_code\diffusion_policy_ur7e/src/dp_ur7e")
NEW=Path(r"G:\毕设\03_code\diffusion_policy_ur7e_refactored/src/dp_ur7e")
def definitions(path):
    tree=ast.parse(path.read_text(encoding="utf-8"))
    return {node.name:node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
pairs=[
("images.py","hardware/camera.py",["decode_rgb_image","resize_for_policy","image_tensor"]),
("frame_store.py","hardware/camera.py",["CameraFrame","FrameStore"]),
("robot.py","hardware/robot_state.py",["ReceiveOnlyRobot"]),
("observations.py","hardware/observations.py",["RobotSample","ObservationHistory"]),
("geometry.py","geometry.py",None),
("motion_safety.py","control/safety.py",None),
("motion_robot.py","control/robot.py",["Feedback","read_feedback","dashboard_status","require_dashboard_ready","GuardedRobot"]),
("recording.py","recording.py",None),
("model.py","inference/policy.py",["sha256_file","validate_model_config","validate_predictions","load_policy"]),
("execution.py","pipeline.py",["prepare_candidate","observation_source_stamp","wait_observation"]),
]
unchanged=[]
for original,target,names in pairs:
    a,b=definitions(OLD/original),definitions(NEW/target)
    for name in names or list(a):
        if ast.dump(a[name],include_attributes=False)!=ast.dump(b[name],include_attributes=False):
            raise AssertionError("kernel AST changed: "+original+":"+name)
        unchanged.append(original+":"+name)
# Session's lazy import is an intentional cycle-breaking change, other methods stay identical.
a=definitions(OLD/"session.py")["SensorSession"]
b=definitions(NEW/"hardware/observations.py")["SensorSession"]
for method in a.body:
    if isinstance(method,ast.FunctionDef) and method.name!="__enter__":
        other=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==method.name)
        assert ast.dump(method,include_attributes=False)==ast.dump(other,include_attributes=False)
        unchanged.append("session.py:SensorSession."+method.name)

def package(name,path):
    spec=importlib.util.spec_from_file_location(name,path/"__init__.py",submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)

package("baseline_dp",OLD)
package("refactored_dp",NEW)
from baseline_dp import images as oi, frame_store as of, geometry as og, observations as oo, motion_safety as os
from refactored_dp.hardware import camera as nc, observations as no
from refactored_dp import geometry as ng
from refactored_dp.control import safety as ns

rng=np.random.default_rng(20261026)
cases=0
for encoding in ["rgb8","bgr8"]:
    raw=rng.integers(0,256,(7,19),dtype=np.uint8)
    message=SimpleNamespace(height=7,width=5,step=19,encoding=encoding,data=raw.tobytes())
    np.testing.assert_array_equal(oi.decode_rgb_image(message),nc.decode_rgb_image(message))
    cases+=1
for shape in [(480,640,3),(301,199,3),(96,96,3)]:
    image=rng.integers(0,256,shape,dtype=np.uint8)
    old,new=oi.resize_for_policy(image),nc.resize_for_policy(image)
    np.testing.assert_array_equal(old,new)
    np.testing.assert_array_equal(oi.image_tensor(old),nc.image_tensor(new))
    cases+=2
for _ in range(100):
    origin=rng.normal(size=3)
    args=(origin,[[1,0,0],[0,1,0]],[1000,1000],[256,256],[0,512])
    old,new=og.PlanarMapping(*args),ng.PlanarMapping(*args)
    point=origin+rng.uniform(-0.1,0.1,3)
    np.testing.assert_array_equal(old.to_model(point),new.to_model(point))
    action=rng.uniform(0,512,2)
    np.testing.assert_array_equal(old.to_base(action),new.to_base(action))
    cases+=2
for _ in range(100):
    pose=np.array([0.3,-0.2,0.4,0.0,3.14,0.0])
    old=os.ActionGuard(pose,os.MotionLimits.visible())
    new=ns.ActionGuard(pose,ns.MotionLimits.visible())
    for index in range(3):
        desired=pose[:3]+rng.normal(size=3)
        a,b=old.propose(desired,pose,source_age_s=0.8),new.propose(desired,pose,source_age_s=0.8)
        np.testing.assert_array_equal(a,b)
        old.commit(a,pose)
        new.commit(b,pose)
        assert old.path_m==new.path_m and old.commands==new.commands
        pose=a
        cases+=1
for _ in range(25):
    origin=np.array([0.3,-0.2,0.4])
    args=(origin,[[1,0,0],[0,1,0]],[1000,1000],[256,256],[0,512])
    old=oo.ObservationHistory(og.PlanarMapping(*args))
    new=no.ObservationHistory(ng.PlanarMapping(*args))
    for index,stamp in enumerate([2.0,2.1]):
        image=rng.integers(0,256,(96,96,3),dtype=np.uint8)
        pose=np.r_[origin+rng.uniform(-.001,.001,3),[0.,3.14,0.]]
        q=np.zeros(6)
        old.add_robot(oo.RobotSample(stamp-.001,100+index,pose[:3],pose,q,1,7))
        new.add_robot(no.RobotSample(stamp-.001,100+index,pose[:3],pose,q,1,7))
        common=(image,index,stamp,100+index,"optical","same")
        old.add_frame(of.CameraFrame(*common))
        new.add_frame(nc.CameraFrame(*common))
    a,ae=old.build(2.12)
    b,be=new.build(2.12)
    for name in a:np.testing.assert_array_equal(a[name],b[name])
    assert ae==be
    cases+=1
report={"critical_definitions_ast_identical":len(unchanged),"definitions":unchanged,
        "differential_cases_passed":cases,"hardware_used":False,
        "checkpoint_deserialized":False,"real_policy_inference":False,
        "intentional_changes":["module imports and resource paths","config schema/CLI","shared predict timing includes conversion/sync in shadow","private backend manifest validation"]}
out=Path(__file__).with_name("equivalence.json")
out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="definitions"},indent=2))

