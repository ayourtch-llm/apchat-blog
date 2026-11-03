#!/usr/bin/env bash
# Writes PROVENANCE.md mechanically from what is on disk (re-run at the end; nothing here is typed by hand except the header).
cd ~/work/wsp
{
echo "# wsp-loop provenance (generated $(date -u +%FT%TZ) by provenance.sh)"
cat <<"H"

## Source
- Idea and reference edit: RikiyaT/lm_understand-logs, commit 4d09ba6d6a7e891dd8063974dfe81b3d78e3494f (2026-10-29),
  folder exp8_math (blog post "Sparks of Weight Space Programming", Experiment 8: Astra edits Qwen3.5-0.8B weights).
  Their final edit "p50c" is reproduced here as ref-p50c (their apply_edit.py, ref/code/).
- Base model: Qwen3.5-0.8B (models/Qwen3.5-0.8B, HF layout).
- Our edits: edit A (edit.py: one direction from layer 22, alpha 1 projection, top-64 columns of L15+L19),
  edit B and sw-* (edit2.py: per-layer repetition direction d_L from acts-250.pt, W <- W - alpha * d_L (d_L^T W) on the
  top-K columns, layers listed in the name). sw-aAkK = alpha A, top-K columns, L15+L19 unless the name says L13-21.
- Directions came from MATH TRAIN problems (collect.py: EleutherAI/hendrycks_math train split, 40 per subject,
  collect-train-8k.jsonl, 280 completions; acts.py -> acts-250.pt). No MATH-500 test problem was used to build any edit.

## Eval protocol
- evalmath.py: MATH-500 (data-math500.jsonl), thinking mode, temperature 0.6, top_p 0.95, top_k 20,
  presence_penalty 1.5, seed = 1000*idx + sample, answer checked with math_verify against the reference answer.
  "hit_limit" = finish_reason length (ran into the token cap, the loop symptom). OFFSET env selects the problem range.
- Server: llama.cpp llama-server, bf16 gguf, -ngl 99, -np 16, context 16 x cap, GPU2 (RTX PRO 6000 Blackwell).
- Text check: llama-perplexity on wiki.test.raw, -c 2048, 60 chunks.
H
echo; echo "## Software"
echo "- llama.cpp: $(git -C ~/llama.cpp log -1 --format="%H %cd")"
echo "- python venv: $(.venv/bin/python --version 2>&1); $(.venv/bin/pip list 2>/dev/null | grep -iE "^(torch|transformers|math.verify|datasets|aiohttp|safetensors|numpy) " | awk "{printf \"%s %s; \", \$1, \$2}")"
echo "- GPU: $(nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader | sed -n 3p)"
echo; echo "## File hashes (sha256)"; echo "\`\`\`"
sha256sum gguf/*.gguf *.py ref/code/*.py *.sh sweep-jobs.txt data-math500.jsonl collect-train-8k.jsonl acts-250.pt ~/models/wiki.test.raw models/Qwen3.5-0.8B/*.safetensors 2>/dev/null
echo "\`\`\`"
echo; echo "## Edit build logs (first lines)"
for f in build-sw-*.log; do echo "- $f: $(grep -E "^layer" $f | tr "\n" ";")"; done
echo; echo "## Runs (one line per result file: summary line from its .log)"; echo "\`\`\`"
for f in *.log; do case $f in logs-server-*|build-*|ppl-*|acts.log|collect.log) continue;; esac; s=$(grep -v ^ERR $f | tail -1); e=$(grep -c ^ERR $f); echo "$f :: $s :: ERR-lines=$e"; done
echo "\`\`\`"
echo; echo "## Perplexity"; echo "\`\`\`"; for f in ppl-*.log; do echo "$f $(grep -o "Final estimate: PPL = [0-9.]* +/- [0-9.]*" $f)"; done; echo "\`\`\`"
echo; echo "## Driver outputs (timestamps per job)"; for f in run-32k.out sweep.out stage3.out stage4.out; do [ -f $f ] && { echo "### $f"; echo "\`\`\`"; cat $f; echo "\`\`\`"; }; done
} > PROVENANCE.md
echo "PROVENANCE.md $(wc -c < PROVENANCE.md) bytes"
