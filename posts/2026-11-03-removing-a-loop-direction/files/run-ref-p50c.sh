#!/usr/bin/env bash
# Positive control: THEIR p50c edit (top64 alpha6, L15+L19) applied to our base, same eval as base/editA.
set -euo pipefail
cd ~/work/wsp
M=models/ref-p50c
rm -rf "$M"; mkdir -p "$M"
for f in models/Qwen3.5-0.8B/*; do b=$(basename "$f"); [ "$b" = model.safetensors-00001-of-00001.safetensors ] || cp "$f" "$M/"; done
.venv/bin/python ref/code/apply_edit.py models/Qwen3.5-0.8B/model.safetensors-00001-of-00001.safetensors ref/runs/p50c/edit "$M/model.safetensors-00001-of-00001.safetensors"
.venv/bin/python ~/llama.cpp/convert_hf_to_gguf.py "$M" --outtype bf16 --outfile gguf/ref-p50c.gguf
CUDA_VISIBLE_DEVICES=0 ~/llama.cpp/build/bin/llama-server -m gguf/ref-p50c.gguf --host 127.0.0.1 --port 8131 -ngl 99 -c 524288 -np 16 > logs-server-ref-p50c.log 2>&1 &
SP=$!; echo "SERVER PID $SP"
until curl -sf localhost:8131/health >/dev/null; do sleep 2; kill -0 $SP; done
.venv/bin/python evalmath.py 8131 ref-p50c-m100x1-16k.jsonl 100 1 16384 > ref-p50c-m100x1-16k.log 2>&1
kill $SP
echo REF-DONE
