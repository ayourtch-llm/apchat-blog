#!/usr/bin/env bash
# 32k run: base vs edit B, MATH-500 first 100 x1, 32768 cap, both on GPU2 in parallel.
set -euo pipefail
cd ~/work/wsp
run() { # NAME GGUF PORT
  CUDA_VISIBLE_DEVICES=2 ~/llama.cpp/build/bin/llama-server -m gguf/$2 --host 127.0.0.1 --port $3 -ngl 99 -c 524288 -np 16 > logs-server-$1-32k.log 2>&1 &
  local SP=$!; echo "$1 SERVER PID $SP"
  until curl -sf localhost:$3/health >/dev/null; do sleep 2; kill -0 $SP; done
  .venv/bin/python evalmath.py $3 $1-m100x1-32k.jsonl 100 1 32768 > $1-m100x1-32k.log 2>&1 || echo "$1 EVAL FAILED"
  kill $SP
  echo "$1 DONE"
}
run base base.gguf 8131 &
run editB editB.gguf 8132 &
wait
echo RUN32K-DONE
