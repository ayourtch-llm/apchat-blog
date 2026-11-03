#!/usr/bin/env bash
# Sweep: (1) ref-p50c at 32k as yardstick, (2) edit-B sweep at 16k. All on GPU2, 4 jobs at a time.
set -uo pipefail
cd ~/work/wsp
# variant name : topk alpha layers
VARS="a4k64:64:4:15 19
a8k64:64:8:15 19
a12k64:64:12:15 19
a4k256:256:4:15 19
a6k256:256:6:15 19
a8k256:256:8:15 19
a6k64L13-21:64:6:13 14 15 16 17 18 19 20 21
a3k64L13-21:64:3:13 14 15 16 17 18 19 20 21"
build() { # NAME TOPK ALPHA LAYERS
  [ -f gguf/sw-$1.gguf ] && return 0
  .venv/bin/python edit2.py acts-250.pt models/sw-$1 $2 $3 $4 > build-sw-$1.log 2>&1 \
  && .venv/bin/python ~/llama.cpp/convert_hf_to_gguf.py models/sw-$1 --outtype bf16 --outfile gguf/sw-$1.gguf >> build-sw-$1.log 2>&1 \
  && rm -rf models/sw-$1 || { echo "BUILD FAILED $1"; return 1; }
}
evaljob() { # NAME GGUF PORT CAP
  CUDA_VISIBLE_DEVICES=2 ~/llama.cpp/build/bin/llama-server -m gguf/$2 --host 127.0.0.1 --port $3 -ngl 99 -c $((16*$4)) -np 16 > logs-server-$1.log 2>&1 &
  local SP=$!
  until curl -sf localhost:$3/health >/dev/null; do sleep 2; kill -0 $SP || { echo "SERVER DIED $1"; return 1; }; done
  .venv/bin/python evalmath.py $3 $1.jsonl 100 1 $4 > $1.log 2>&1 || echo "EVAL FAILED $1"
  kill $SP; wait $SP 2>/dev/null
  echo "DONE $1 $(grep -v ^ERR $1.log | tail -1)"
}
echo "START $(date)"
while IFS=: read n k a l; do build "$n" "$k" "$a" "$l"; done <<< "$VARS"
echo "BUILT $(date)"
{ echo "ref-p50c-m100x1-32k ref-p50c.gguf 32768"
  while IFS=: read n k a l; do echo "sw-$n-m100x1-16k sw-$n.gguf 16384"; done <<< "$VARS"; } > sweep-jobs.txt
i=0; pids=()
while read name g cap; do
  port=$((8141 + i % 4))
  # wait for a free slot: at most 4 jobs
  while [ $(jobs -rp | wc -l) -ge 4 ]; do sleep 10; done
  # a port is free once its previous job ended; reuse round-robin only after its job is gone
  while curl -sf localhost:$port/health >/dev/null 2>&1; do port=$((8141 + (port - 8141 + 1) % 4)); sleep 1; done
  evaljob $name $g $port $cap &
  i=$((i+1)); sleep 20
done < sweep-jobs.txt
wait
echo "SWEEP-DONE $(date)"
