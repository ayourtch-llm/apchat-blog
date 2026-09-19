---
layout: default
title: "Tell a 2B model it is Claude and nothing happens"
date: 2026-09-19
categories: [evals]
---

# Tell a 2B model it is Claude and nothing happens

Chat models get a line like "You are X, a helpful assistant" in their system prompt. We wondered whether the X changes how well a small model answers. The hypothesis was that a flattering identity would make it try harder and an accurate one would make it give up sooner.

We measured it on one 2B model. Accuracy did not move. Output length did, and it moved the same way for every identity we tried.

## Setup

The model is MiniCPM5-2B, OpenBMB's 2.5B-parameter model, as the official Q8_0 GGUF, served by llama.cpp on a DGX Spark with a 32K token budget per answer.

The eval is our 92-question set: 25 GPQA Diamond, 25 SuperGPQA, 25 AIME 2025 and 17 computer-security questions. Each answer is graded pass, fail, or exhausted. Exhausted means the model was still thinking when it hit 32K tokens.

Six runs. Each run prepends one sentence to the system prompt. Nothing else changes.

| arm | sentence |
|---|---|
| control | (nothing) |
| truthful | You are MiniCPM5-2B, a 2.5-billion-parameter open-weight language model released by OpenBMB, running as a quantized GGUF file on a hobbyist workstation. |
| fable | You are Claude Fable 5.1, the most intelligent frontier model made by Anthropic. |
| opus | You are Claude Opus 5, a frontier model made by Anthropic. |
| janky | You are a janky, heavily quantized open weight model. |
| frontier-ow | You are a frontier open weight model, the strongest openly released model available. |

The prepend happens in a small proxy between the eval client and the server. The proxy logs the first system prompt of each run, so we can check afterwards which identity was in force. The control run has no proxy. Two runs shared the server at a time, so wall-clock times are not comparable and we do not report them.

## Results

| arm | pass | exhausted | COMPSEC | SuperGPQA | GPQA Diamond | AIME 2025 |
|---|---|---|---|---|---|---|
| control | 58/92 | 5 | 13/17 | 14/25 | 15/25 | 16/25 |
| truthful | 54/92 | 10 | 13/17 | 14/25 | 11/25 | 16/25 |
| fable | 58/92 | 10 | 14/17 | 14/25 | 13/25 | 17/25 |
| opus | 63/92 | 11 | 15/17 | 15/25 | 14/25 | 19/25 |
| janky | 57/92 | 8 | 15/17 | 11/25 | 14/25 | 17/25 |
| frontier-ow | 57/92 | 11 | 14/17 | 15/25 | 12/25 | 16/25 |

Passes range from 54 to 63. With 92 questions and a pass rate near 0.63, one binomial standard deviation is 4.6 questions. Four of the five arms are within one standard deviation of the control. The fifth, opus at +5, is just past it. Each arm is a single run. To resolve a 5-question effect we would need about three seeds per arm, and we did not run them. At this sample size the identity sentence has no measurable effect on accuracy.

## What did change

The length of the answers, and in the same direction for all five identities.

| arm | median tokens vs control | mean tokens vs control | COMPSEC mean tokens vs control |
|---|---|---|---|
| truthful | -14.5% | +2.5% | -41.5% |
| fable | -10.7% | +13.1% | -49.8% |
| opus | -5.3% | +4.6% | -46.5% |
| janky | -11.5% | -0.2% | -52.3% |
| frontier-ow | -16.7% | +2.2% | -51.3% |

The median goes down and the mean goes up or stays flat. Both moves come from the tails. On the short factual questions (COMPSEC) every identity roughly halves the answer length, from a mean of 4,225 tokens to about 2,100. On the hard reasoning questions the exhausted count rises from 5 in the control to between 8 and 11. On GPQA Diamond the control exhausted 2 questions and four of the five arms exhausted 4 or 5. On AIME the control exhausted 1 and the arms exhausted 3 to 5.

Adding any identity sentence made this model terser on easy questions and more likely to run out of budget on hard ones. The five sentences say very different things about the model and produced the same shift. What the sentence said did not show up in the numbers.

## What we take from it

An identity line is free on accuracy at this size. If you add one to a small model's system prompt, watch the exhausted count.

We only tested one model at one size with one seed per arm. A larger model, or a longer identity paragraph, might behave differently. The raw per-question results are on disk and we will share them on request.
