#!/usr/bin/env python3
"""Project the loop direction out of chosen MLP down_proj output columns and save a new model dir.
usage: edit.py ACTS.pt DIR_LAYER OUTDIR TOPK LAYER [LAYER...]
d = unit(mean residual after DIR_LAYER, loop tokens  -  same, pre-loop tokens).
For each LAYER: score columns j of down_proj by |d . W[:, j]|, take the TOPK largest
(TOPK=0 means all columns), and set W[:, j] -= d (d . W[:, j]) for those columns."""
import json, shutil, sys, os, torch
from safetensors.torch import load_file, save_file
acts, dl, outdir, topk = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
layers = [int(x) for x in sys.argv[5:]]
SRC = "models/Qwen3.5-0.8B"
m = torch.load(acts)["mean"]
d = (m["res_loop"][dl] - m["res_pre"][dl]).float(); d = d / d.norm()
if os.path.exists(outdir): shutil.rmtree(outdir)
shutil.copytree(SRC, outdir, ignore=shutil.ignore_patterns("*.safetensors", ".cache"))
f = "model.safetensors-00001-of-00001.safetensors"
sd = load_file(f"{SRC}/{f}")
changed = 0
for L in layers:
    k = f"model.language_model.layers.{L}.mlp.down_proj.weight"
    W = sd[k].float()                       # [hidden, intermediate]
    c = d @ W                               # [intermediate]
    idx = torch.argsort(c.abs(), descending=True)[:topk] if topk else torch.arange(W.shape[1])
    before = c[idx].abs().mean().item()
    W[:, idx] -= torch.outer(d, c[idx])
    after = (d @ W)[idx].abs().mean().item()
    sd[k] = W.to(sd[k].dtype)
    changed += W.shape[0] * len(idx)
    print(f"layer {L}: {len(idx)} columns, mean |d.w| {before:.4f} -> {after:.4f}")
save_file(sd, f"{outdir}/{f}", metadata={"format": "pt"})
print(f"changed {changed} weights; direction from residual after layer {dl}")
