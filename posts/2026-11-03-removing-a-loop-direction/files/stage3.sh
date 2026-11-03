#!/usr/bin/env bash
# Stage 3: 16k sweep could not separate settings (all 5-13%, ~90% hit the cap), so the 3 nearest
# neighbours of edit B go to 32k, and every model gets a wiki perplexity check (normal text not harmed?).
set -uo pipefail
cd ~/work/wsp
evaljob() { # NAME GGUF PORT CAP
  CUDA_VISIBLE_DEVICES=2 ~/llama.cpp/build/bin/llama-server -m gguf/$2 --host 127.0.0.1 --port $3 -ngl 99 -c $((16*$4)) -np 16 > logs-server-$1.log 2>&1 &
  local SP=$!
  until curl -sf localhost:$3/health >/dev/null; do sleep 2; kill -0 $SP || { echo "SERVER DIED $1"; return 1; }; done
  .venv/bin/python evalmath.py $3 $1.jsonl 100 1 $4 > $1.log 2>&1 || echo "EVAL FAILED $1"
  kill $SP; wait $SP 2>/dev/null
  echo "DONE $1 $(grep -v ^ERR $1.log | tail -1)"
}
echo "START $(date)"
for m in base editB ref-p50c sw-a4k256 sw-a8k64 sw-a6k256 sw-a4k64; do
  CUDA_VISIBLE_DEVICES=2 ~/llama.cpp/build/bin/llama-perplexity -m gguf/$m.gguf -f ~/models/wiki.test.raw -ngl 99 -c 2048 --chunks 60 > ppl-$m.log 2>&1
  echo "PPL $m $(grep -o "Final estimate: PPL = [0-9.]* +/- [0-9.]*" ppl-$m.log)"
done
evaljob sw-a4k256-m100x1-32k sw-a4k256.gguf 8141 32768 &
sleep 20; evaljob sw-a8k64-m100x1-32k sw-a8k64.gguf 8142 32768 &
sleep 20; evaljob sw-a6k256-m100x1-32k sw-a6k256.gguf 8143 32768 &
wait
echo "STAGE3-DONE $(date)"
