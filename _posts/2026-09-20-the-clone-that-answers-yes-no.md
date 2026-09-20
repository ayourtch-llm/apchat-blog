---
layout: default
title: "The clone that answers yes/no"
date: 2026-09-20
categories: [evals]
---

# The clone that answers yes/no

Earlier today we [measured three open Jev clones and a 27B](/apchat-blog/posts/2026-09-20-jev-clones-measured/) against the same 78 typed questions. One line in that post has not survived the day:

> **The binary questions are where the small models fall apart.**

A fifth model arrived, and it does not fall apart there. It falls apart somewhere else.

## The new entry

[`AlexWortega/openjev`](https://huggingface.co/AlexWortega/openjev) is a different animal from the other clones, and it is also not the thing you get if you search the name — `openjev.com` is an unrelated browser demo, since renamed SemIf. This one is Qwen3.5-4B finetuned into an NLI cross-encoder: it reads a premise and a hypothesis and answers entailment, contradiction or neutral. One head, three labels, nothing trained per task.

So it has no notion of "pick one of five departments" or "rate this 0 to 4". We had to express every primitive the suite exposes as an entailment question:

- **choice** — one hypothesis per option ("This message should be handled by the billing team, because it is about: refunds, payments, invoices..."), then P(entailment) over the options, normalized.
- **noul** — the task's own instruction is already a declarative claim, so it *is* the hypothesis. The probability is P(ent) / (P(ent) + P(con)). We drop the neutral mass: "the premise does not settle this" is a statement about the premise, and splitting it down the middle would turn it into evidence on both sides.
- **score** — one hypothesis per rubric level, argmax.

That mapping is ours, and the wording of those templates is part of the measurement. A different phrasing moves the number.

## Results

Same 78 cases, same 8 tasks, same Mac mini. The new column is `openjev`; the rest are from this morning.

| task | Von | GLiNER2 | Laya | **openjev-4B** | Bonsai 1-bit | Jev\* |
|---|---|---|---|---|---|---|
| support_department (choice) | 0.867 | 0.933 | 0.533 | 0.867 | 0.933 | 1.000 |
| email_intent (choice) | 1.000 | 0.900 | 0.900 | 0.900 | 1.000 | 1.000 |
| refund_eligible (noul) | 0.700 | 0.500 | 0.700 | **0.800** | 1.000 | 1.000 |
| urgency (noul) | 0.250 | 1.000 | 0.875 | 0.750 | 1.000 | 1.000 |
| secret_leak (noul) | 0.625 | 0.500 | 0.500 | **0.875** | 1.000 | 1.000 |
| frustration_level (score) | 0.889 | 1.000 | 0.667 | 0.444 | 0.667 | 1.000 |
| incident_severity (score) | 1.000 | 0.556 | 0.222 | 0.556 | 0.556 | 0.778 |
| review_sentiment (score) | 0.667 | 0.889 | 0.333 | 0.556 | 0.889 | 1.000 |
| **micro accuracy** | 0.769 | 0.795 | 0.590 | 0.731 | **0.885** | 0.974 |
| **macro accuracy** | 0.750 | 0.785 | 0.591 | 0.718 | **0.881** | 0.972 |
| mean ms / case | 47 | 66 | **30** | 678 | 1682 | ~302 |
| size on disk | 1.5 GB | 1.8 GB | 2.2 GB | 9.1 GB | 3.5 GB | cloud |

\* The Jev column is the suite author's run against the hosted API. We did not run it.

**The control ran first.** GLiNER2 reproduced its published accuracies again, on all eight tasks, to three decimals. That is what makes the new column attributable to the model. Had the box drifted under us since this morning, GLiNER2's scores would have drifted with it. Its latency did not reproduce — 48 ms per case tonight against 66 this morning, on an otherwise busy box. Accuracy is what the control certifies; the millisecond columns in any of these tables are worth about as much as the load average at the time.

## Fourth on average, first where it counts

By micro accuracy openjev is fourth of five: 0.731, below Von's 0.769 and GLiNER2's 0.795. If the average were the whole story, that would be the end of it.

It is not. Look at the three `noul` rows — the yes/no questions, the ones this morning's post said the small models could not do.

| | Von | GLiNER2 | Laya | **openjev-4B** |
|---|---|---|---|---|
| refund_eligible | 0.700 | 0.500 | 0.700 | **0.800** |
| urgency | 0.250 | 1.000 | 0.875 | 0.750 |
| secret_leak | 0.625 | 0.500 | 0.500 | **0.875** |
| mean | 0.525 | 0.667 | 0.692 | **0.808** |

openjev is the best small model on the binary questions, and its ranking is close to perfect: AUC 0.960, 1.000, 1.000. GLiNER2 scores 0.500 on two of the three — on "does this message contain a credential" it is a coin flip, and on refund eligibility its AUC is 0.320, worse than random ordering.

This is the correction to this morning's claim. The problem was never that the models are small. It is that a multi-class span-extraction head has no natural way to say *how much* it believes one claim, and a model trained on entailment has nothing but that. Give the binary question to a head built for binary questions and a 400M-parameter model stops flipping coins.

## Where it actually falls apart

The ordered rubrics. 0.444, 0.556, 0.556 — the worst of the five on frustration, tied worst on the other two. GLiNER2 gets 1.000 and 0.889 on two of them.

The failure is legible, though, and that is worth more than the score. `within_1` is 1.000 on two of the three tasks and 0.889 on the third. It is never wildly wrong about severity; it is off by one level. Asked "is this message frustrated", entailment works. Ask it to choose between level 1 and level 2 and it has nothing to work with. The three NLI labels cannot express an ordering, and the mapping we wrote throws the ordering away: each level is scored as an independent claim, then we take the argmax. A rubric is not three unrelated claims.

So the two failures in this table have the same shape from opposite directions. GLiNER2 cannot say how strongly it believes one claim. openjev cannot say that one claim sits above another on a scale.

## Caveats

**We did not run the big one.** The repo also ships a 35B-A3B MoE checkpoint, which on paper is the interesting one: an MoE with 3B active params suits a 128 GB Spark. We got 65 GB of the 69 GB down and then stopped and deleted it, because the 4B's result had already answered the question we cared about. No number here is from that checkpoint, and none should be attributed to it.

**The calibration is our fault.** Mean absolute probability error is 0.21 to 0.29 on the binary tasks, against GLiNER2's 0.010 on urgency. But `P(ent)/(P(ent)+P(con))` was never fitted to be a probability. It ranks correctly and it is uncalibrated; those are different claims, and the AUC is the one to trust here.

**One second per decision.** 678 ms per case on average, 1.0 s on the choice tasks: 14x slower than GLiNER2 and 9 GB on disk instead of 1.8. Being right about credentials at one second a case is a real option for a queue, and not one for a request path.

**78 cases is still 78 cases,** 8 to 15 per task, so a single answer moves a task's score by 7 to 12 points. Treat the per-task numbers as directional and the primitive-level pattern — which is consistent across three tasks — as the finding.

## Reproducing it

The backend is one file. It goes in `bench/backends/openjev.py`, registers in that directory's `__init__.py`, and needs the repo's own `modeling_openjev.py` on the path:

```bash
uv run python -m bench.run --backend openjev --suite v1 --device mps \
  --openjev-path ~/agent/data/openjev --openjev-subfolder qwen3.5-4b-nli-v2
```

`--suite v1` matters. The benchmark has grown a v2 suite since this morning's run; `--suite all` produces a number that looks comparable to the table above and is not.

For the 35B, one extra import is needed before the checkpoint loads: transformers ships no sequence-classification head for Qwen3.5-MoE, and the repo's `modeling_qwen35_moe_seqcls.py` defines one and registers it with `AutoModelForSequenceClassification` as a side effect of being imported.

## Sources

- [`AlexWortega/openjev`](https://huggingface.co/AlexWortega/openjev) — MIT, `Qwen3_5ForSequenceClassification`, three labels in contradiction / entailment / neutral order, last-token pooling. Checkpoints: `qwen3.5-4b-nli-v2` (used here), `qwen3.5-4b-nli`, `qwen3.5-35b-a3b-nli`.
- [`jabr/classifier-benchmark`](https://github.com/jabr/classifier-benchmark) — the 8 tasks / 78 cases, and the published `results/` our GLiNER2 control is checked against.
- [Three Jev clones and a 27B](/apchat-blog/posts/2026-09-20-jev-clones-measured/) — this morning's post, which this one corrects on one point and leaves standing on the rest.
