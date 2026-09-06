---
layout: default
title: "27 tok/s from a 320B model on one DGX Spark"
date: 2026-09-06
categories: [ai, llm, benchmarks]
---

# 27 tok/s from a 320B model on one DGX Spark

We serve GLM-5.3-Flash at home. It is a 320B-parameter mixture-of-experts model, about 18B active per token: 288 routed experts, 8 used per token, plus one shared expert. Until this weekend it ran as a Q4_K_XL quant split across two DGX Spark units (GB10, 119 GB unified memory each) over RPC. That setup delivered about 15 tokens per second on real question-answering work.

Today we adopted a config that delivers 27 tok/s on the same eval, on a single Spark, with 256K context loaded. This post is the story of how we got there, including the two dead ends. The dead ends did most of the teaching.

## The eval gate

Speed claims are cheap. Our rule: a serving config change must not make eval results worse. The harness runs 92 audited cases (GPQA-Diamond, SuperGPQA, AIME2025, and an internal security set), fixed seed, fixed thinking budget, sequential requests. It reports pass/fail/exhausted per case, plus token and byte counts. "Exhausted" means the model hit the token budget before answering — the direct measure of a model that has started to ramble.

The baseline, Q4_K_XL over two Sparks with multi-token prediction (MTP) at draft depth 2: **72/92 passes, 4 exhausted, 10,692 seconds of request time, 15.05 delivered tok/s.**

## Dead end one: exact-token equality

The first speed campaign ran under a strict gate: the optimized config had to produce byte-identical output. That gate rejected everything, including a graph-reuse build already measuring 23-24 tok/s on greedy screens (27 on repetitive filler fixtures). Correct call at the time — but it turned out we were guarding the wrong invariant. Nobody needs identical bytes. They need answers that are as correct, delivered sooner.

## Dead end two: the mislabeled candidate

We relaxed the gate to "not worse on the eval: no fewer passes, no longer answers." A delegated agent ran a full day of candidates against it. Two finalists both failed: 71/92 versus 72, and much longer answers (+37% and +56% visible-answer bytes). Report filed, household config unchanged.

Then two things surfaced in the post-mortem.

First, the accuracy delta was noise. The paired per-case diff showed 4-6 baseline passes lost and 3-5 non-passes gained, either direction, net one case. A single fixed-seed run cannot distinguish that from run-to-run churn.

Second — and this is the embarrassing one — the finalist named "F16-KV" was not the household config with one flag changed. Its registration file showed a different quant (Q2_K_XL instead of Q4_K_XL), a single node instead of two, and 70K context instead of 128K. The speed came mostly from the smaller quant and from dropping the RPC hop, not from the KV dtype in its name. Lesson, now filed in the wiki: **read the candidate's registration before proposing adoption. The name undersells; the config file doesn't.**

## The reframe

The gate got redefined around what we actually care about: correctness within churn noise, wall-clock time to finish the eval, and exhaustion count not worse. Under that metric the picture inverted. The rejected candidate had finished the same 92 cases in 6,347 seconds instead of 10,692 — 41% less waiting — with the same exhaustion count and a one-case accuracy delta inside the noise band.

So we tested a clean version of it deliberately: UD-Q2_K_XL (the published quant, not a home requant — this matters, see below), f16 KV cache, MTP depth 2, one Spark, and pushed the context up instead of down.

## The adopted config

- **Model:** GLM-5.3-Flash UD-Q2_K_XL (~102 GiB on disk)
- **One GB10 Spark**, no RPC
- **Context:** 262,144 tokens loaded, 117 GB of 119 GB used
- **KV cache:** f16; **MTP** draft depth 2

Measured, with random-word documents as the depth filler (see the measurement note below). The shallow and 43K rows are from the same serve at 131K loaded context; the 256K serve measured 27.2 shallow and the 190K row:

| Depth | Generation |
|---|---:|
| shallow | 27.2–27.65 tok/s |
| 43K tokens | 27.85 tok/s |
| 190K tokens | 19.8 tok/s |

No sag at all out to 43K; past ~130K it bends, and at 190K you still get 19.8. Prefill averaged 141.7 tok/s over a 190K prompt — 22 minutes to ingest, so you plan around long-context prefill, not around generation. A verbatim-retrieval probe at 190K depth came back accurate.

The full-eval numbers (27.65 delivered tok/s, wall time 6,347 vs 10,692 seconds, passes within noise of baseline, exhaustion equal) are from the 70K-context candidate run; the adopted config is the same model, build and flags with a larger context allocation, and has passed depth, prefill and verbatim-retrieval probes rather than a fresh full eval. Adopted, with the obvious escape hatch: if a task ever needs the Q4 quality margin, the two-Spark config is one relaunch away.

## Why this works at all

Three things line up.

**The KV cache is tiny.** GLM-5.3-Flash is a hybrid: of its 46 blocks, only 12 carry a conventional (MLA) KV cache. The other 34 are linear-attention layers with constant-size state. That is roughly 14 KB per token at f16 — a 256K context costs ~3.5 GiB, not the tens of GB a dense-attention 320B model would want. Cranking context to 256K on a 119 GB box next to 102 GB of weights is only possible because of this.

**MTP works — if the head is healthy.** The model ships a multi-token-prediction layer, and llama.cpp's draft-mtp mode (PR #27754 lineage) uses it as a built-in speculative draft. At depth 2 we see 1.5x on this hardware. We first measured MTP as useless (~45% draft acceptance, breakeven) and nearly wrote it off. The culprit was our own requant: it had crushed the MTP head's projection tensor to Q2_K. The published UD quants keep that tensor at Q8_0; with the healthy head, acceptance jumped to 0.59–0.71 and the 1.5x appeared. If you requant a model with an MTP head, protect the head.

**Depth 2, not more.** Draft depth 3 gave the entire gain back on an offload-heavy config: acceptance dropped and the larger verify batch cost more than the extra draft token earned. Also a measurement note: repetitive filler text inflates MTP throughput by ~4% because the draft head predicts repetition well. Use random-word documents to measure depth behavior.

## What the numbers are not

One fixed-seed eval run is a regression screen, not a confidence interval. The 72-versus-71 deltas here are churn; we treat them as such, and we would treat a 72-versus-68 the same way only after a repeat run. And Q2 versus Q4 quality on tasks outside this eval is not settled — that is exactly why the fallback config stays documented.

The next campaign has a sharper target: faster *and* more correct, both at once. The current config leaves an obvious lever — 2 GB of headroom and a quant ladder between Q2 and Q4 — and some unfinished business: a packed expert-slot CUDA kernel that passed 284 correctness checks with promising microbenchmarks but no end-to-end win yet. We'll see what survives the gate.
