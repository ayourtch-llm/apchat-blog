#!/usr/bin/env bash
# Positive control: THEIR p50c edit (top64 alpha6, L15+L19) applied to our base, same eval as base/editA.
set -euo pipefail
cd ~/work/wsp
M=models/edit-B-perlayer-a6
rm -rf "$M"
.venv/bin/python edit2.py acts-250.pt $M 64 6 15 19
.venv/bin/python ~/llama.cpp/convert_hf_to_gguf.py "$M" --outtype bf16 --outfile gguf/editB.gguf
CUDA_VISIBLE_DEVICES=0 ~/llama.cpp/build/bin/llama-server -m gguf/editB.gguf --host 127.0.0.1 --port 8131 -ngl 99 -c 524288 -np 16 > logs-server-editB.log 2>&1 &
SP=$!; echo "SERVER PID $SP"
until curl -sf localhost:8131/health >/dev/null; do sleep 2; kill -0 $SP; done
.venv/bin/python evalmath.py 8131 editB-m100x1-16k.jsonl 100 1 16384 > editB-m100x1-16k.log 2>&1
kill $SP
echo EDITB-DONE
