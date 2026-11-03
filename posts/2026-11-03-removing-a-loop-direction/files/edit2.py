#!/usr/bin/env python3
"""Edit B: per-layer loop direction, scaled subtraction (the p50c recipe, with OUR directions).
usage: edit2.py ACTS.pt OUTDIR TOPK ALPHA LAYER [LAYER...]
For each LAYER L: d_L = unit(mean residual after layer L, loop tokens - same, pre-loop tokens);
score down_proj columns j by |d_L . W[:, j]|, take the TOPK largest, set W[:, j] -= ALPHA * d_L (d_L . W[:, j]).
ALPHA 1 = projection (edit A's strength); p50c used 6. Prints overlap with models/ref-p50c's edited columns."""
import shutil, sys, os, torch
from safetensors.torch import load_file, save_file
acts, outdir, topk, alpha = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
layers = [int(x) for x in sys.argv[5:]]
SRC, REF = "models/Qwen3.5-0.8B", "models/ref-p50c"
f = "model.safetensors-00001-of-00001.safetensors"
m = torch.load(acts)["mean"]
if os.path.exists(outdir): shutil.rmtree(outdir)
shutil.copytree(SRC, outdir, ignore=shutil.ignore_patterns("*.safetensors", ".cache"))
sd = load_file(f"{SRC}/{f}")
ref = load_file(f"{REF}/{f}") if os.path.exists(f"{REF}/{f}") else None
for L in layers:
    d = (m["res_loop"][L] - m["res_pre"][L]).float(); d = d / d.norm()
    k = f"model.language_model.layers.{L}.mlp.down_proj.weight"
    W = sd[k].float()
    c = d @ W
    idx = torch.argsort(c.abs(), descending=True)[:topk]
    W[:, idx] -= alpha * torch.outer(d, c[idx])
    sd[k] = W.to(sd[k].dtype)
    msg = f"layer {L}: {len(idx)} columns, alpha {alpha}"
    if ref is not None:
        rc = set(((ref[k].float() - load_file(f'{SRC}/{f}')[k].float()).abs().sum(0) > 0).nonzero().flatten().tolist())
        msg += f", overlap with p50c columns {len(rc & set(idx.tolist()))}/{len(idx)}"
    print(msg, flush=True)
save_file(sd, f"{outdir}/{f}", metadata={"format": "pt"})
