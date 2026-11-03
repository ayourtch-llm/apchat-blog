#!/usr/bin/env python3
"""Mean activations, before vs after the loop starts, in the SAME looping completions.
usage: acts.py COLLECT.jsonl OUT.pt [MAX_SEQ]
Loop onset = first token position whose next W tokens occur again later in the completion
(exact token repeat). 'pre' = completion tokens before onset; 'loop' = tokens from onset+W on.
Per layer we sum the residual stream after the layer and the MLP output, per class."""
import json, sys, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
src, out = sys.argv[1], sys.argv[2]
MAXSEQ = int(sys.argv[3]) if len(sys.argv) > 3 else 8192
W = 32
M = "models/Qwen3.5-0.8B"
tok = AutoTokenizer.from_pretrained(M)
model = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16).cuda().eval()
layers = model.model.layers if hasattr(model.model, "layers") else model.model.language_model.layers
L = len(layers)
cap = {}
hooks = []
for i, l in enumerate(layers):
    hooks.append(l.mlp.register_forward_hook(lambda m, a, o, i=i: cap.__setitem__(("mlp", i), o[0].float())))
    hooks.append(l.register_forward_hook(lambda m, a, o, i=i: cap.__setitem__(("res", i), (o[0] if isinstance(o, tuple) else o)[0].float())))
H = model.config.get_text_config().hidden_size
S = {(k, c): torch.zeros(L, H, device="cuda") for k in ("mlp", "res") for c in ("pre", "loop")}
N = {"pre": 0, "loop": 0}
def onset(ids):
    first, last = {}, {}
    for t in range(len(ids) - W + 1):
        k = tuple(ids[t:t + W]); first.setdefault(k, t); last[k] = t
    hits = [first[k] for k in first if last[k] - first[k] >= W]
    return min(hits) if hits else None
used = 0
for line in open(src):
    r = json.loads(line)
    if r["finish"] != "length":
        continue
    p = tok.apply_chat_template([{"role": "user", "content": r["prompt"]}], tokenize=False,
                                add_generation_prompt=True, enable_thinking=True)
    pid = tok(p, add_special_tokens=False)["input_ids"]
    cid = tok(r["reasoning"], add_special_tokens=False)["input_ids"]
    ids = (pid + cid)[:MAXSEQ]
    comp = ids[len(pid):]
    o = onset(comp[:4096])
    if o is None or o < 64:
        print(f"skip idx={r['idx']}: onset={o}", file=sys.stderr); continue
    with torch.no_grad():
        model(torch.tensor([ids]).cuda())
    a, b = len(pid), len(pid) + o
    c = b + W
    for k in ("mlp", "res"):
        for i in range(L):
            x = cap[(k, i)]
            S[(k, "pre")][i] += x[a:b].sum(0)
            S[(k, "loop")][i] += x[c:].sum(0)
    N["pre"] += b - a; N["loop"] += len(ids) - c
    used += 1
    print(f"idx={r['idx']} onset={o} pre={b-a} loop={len(ids)-c}", file=sys.stderr)
mean = {f"{k}_{c}": (S[(k, c)] / N[c]).cpu() for k in ("mlp", "res") for c in ("pre", "loop")}
torch.save({"mean": mean, "N": N, "used": used}, out)
print("used", used, "completions; tokens", N)
