#!/usr/bin/env bash
# Stage 4: held-out tests, with full provenance.
# T1 held-out: MATH-500 idx 100-499 (never scored before) at 32k, 1 sample, base / editB / sw-a4k256 / ref-p50c, 4 in parallel on GPU2.
# T2: sw-a4k64 (lowest wiki ppl) at 32k on idx 0-99, the one setting never run at the full cap.
set -uo pipefail
cd ~/work/wsp
evaljob() { # NAME GGUF PORT CAP N OFFSET
  echo "BEGIN $1 $(date -u +%FT%TZ) gguf=$2 cap=$4 n=$5 offset=$6"
  CUDA_VISIBLE_DEVICES=2 ~/llama.cpp/build/bin/llama-server -m gguf/$2 --host 127.0.0.1 --port $3 -ngl 99 -c $((16*$4)) -np 16 > logs-server-$1.log 2>&1 &
  local SP=$!
  until curl -sf localhost:$3/health >/dev/null; do sleep 2; kill -0 $SP || { echo "SERVER DIED $1"; return 1; }; done
  OFFSET=$6 .venv/bin/python evalmath.py $3 $1.jsonl $5 1 $4 > $1.log 2>&1 || echo "EVAL FAILED $1"
  kill $SP; wait $SP 2>/dev/null
  echo "DONE $1 $(date -u +%FT%TZ) $(grep -v ^ERR $1.log | tail -1)"
}
echo "START $(date -u +%FT%TZ)"
evaljob base-h400-32k base.gguf 8151 32768 400 100 &
sleep 20; evaljob editB-h400-32k editB.gguf 8152 32768 400 100 &
sleep 20; evaljob sw-a4k256-h400-32k sw-a4k256.gguf 8153 32768 400 100 &
sleep 20; evaljob ref-p50c-h400-32k ref-p50c.gguf 8154 32768 400 100 &
wait
evaljob sw-a4k64-m100x1-32k sw-a4k64.gguf 8155 32768 100 0
echo "STAGE4-DONE $(date -u +%FT%TZ)"
