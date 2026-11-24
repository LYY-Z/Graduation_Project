"""Verified upstream policy loading and a shared inference-only prediction wrapper."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ALLOWED_POLICIES = {
    "diffusion_policy.policy.diffusion_transformer_hybrid_image_policy.DiffusionTransformerHybridImagePolicy",
    "diffusion_policy.policy.diffusion_unet_hybrid_image_policy.DiffusionUnetHybridImagePolicy",
}


def sha256_file(path) -> str:
    result = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def validate_model_config(cfg):
    shape = cfg["shape_meta"]
    expected = {"image": [3, 96, 96], "agent_pos": [2]}
    if set(shape["obs"]) != set(expected):
        raise ValueError("checkpoint must have exactly image and agent_pos observations")
    for name, value in expected.items():
        if list(shape["obs"][name]["shape"]) != value:
            raise ValueError(f"incompatible observation shape for {name}")
    if list(shape["action"]["shape"]) != [2]:
        raise ValueError("checkpoint must predict two-dimensional actions")
    if cfg["policy"]["_target_"] not in ALLOWED_POLICIES:
        raise ValueError("checkpoint policy architecture is not supported by this adapter")
    if (
        int(cfg["n_obs_steps"]) != 2
        or int(cfg["horizon"]) < int(cfg["n_action_steps"]) + 1
        or int(cfg["n_action_steps"]) < 1
    ):
        raise ValueError("invalid prediction/observation horizon")


def validate_predictions(output, horizon, n_action_steps):
    for name, shape in {
        "action": (1, int(n_action_steps), 2),
        "action_pred": (1, int(horizon), 2),
    }.items():
        array = np.asarray(output[name])
        if array.shape != shape or not np.all(np.isfinite(array)):
            raise ValueError(f"{name} must have finite values and shape {shape}")


def load_policy(cfg):
    """Deserialize verified official weights and load EMA strictly; never called by tests."""
    paths = cfg["paths"]
    manifest = json.loads(paths["checkpoint_manifest"].read_text(encoding="utf-8"))
    if (
        paths["checkpoint"].stat().st_size != manifest["bytes"]
        or sha256_file(paths["checkpoint"]) != manifest["sha256"]
    ):
        raise ValueError("checkpoint size or SHA-256 mismatch")
    sys.path.insert(0, str(paths["upstream"]))
    import dill
    import hydra
    import torch
    from omegaconf import OmegaConf

    with paths["checkpoint"].open("rb") as f:
        payload = torch.load(f, map_location="cpu", pickle_module=dill)
    checkpoint_cfg = payload["cfg"]
    contract = {
        "shape_meta": OmegaConf.to_container(checkpoint_cfg.shape_meta, resolve=True),
        "policy": {"_target_": checkpoint_cfg.policy._target_},
        "n_obs_steps": checkpoint_cfg.n_obs_steps,
        "horizon": checkpoint_cfg.horizon,
        "n_action_steps": checkpoint_cfg.n_action_steps,
    }
    validate_model_config(contract)
    policy = hydra.utils.instantiate(checkpoint_cfg.policy)
    state_key = "ema_model" if checkpoint_cfg.training.use_ema else "model"
    policy.load_state_dict(payload["state_dicts"][state_key], strict=True)
    # The embedded normalizer is retained, including its learned dataset ranges.
    policy.to(torch.device(cfg["inference"]["device"]))
    policy.eval()
    if policy.n_obs_steps != cfg["observation"]["n_obs_steps"]:
        raise ValueError("platform and checkpoint observation horizons disagree")
    details = {
        **contract,
        "weights_key": state_key,
        "checkpoint_sha256": manifest["sha256"],
        "num_inference_steps": int(policy.num_inference_steps),
        "scheduler": type(policy.noise_scheduler).__name__,
    }
    return policy, details


def predict(policy, observation, *, synchronize_cuda=False):
    """Predict original policy outputs without normalizing or clipping them twice.

    Inputs are NumPy observation arrays; outputs retain upstream action units.
    Optional CUDA synchronization supports comparable host-side timing.
    """
    import torch

    tensors = {
        k: torch.from_numpy(v).to(device=policy.device, dtype=policy.dtype)
        for k, v in observation.items()
    }
    if synchronize_cuda and policy.device.type == "cuda":
        torch.cuda.synchronize(policy.device)
    with torch.inference_mode():
        result = policy.predict_action(tensors)
    return {k: result[k].detach().cpu().numpy() for k in ["action", "action_pred"]}
