---
layout: default
title: "Precision settings for the tensorfold GLM-5.3 recipe"
date: 2026-10-03 11:04:00 +0200
categories: [evals]
---

# Precision settings for the tensorfold GLM-5.3 recipe

The [GLM-5.3-Flash EXL3 TensorFold recipe](https://github.com/MiaAI-Lab/GLM-5.3-Flash-EXL3-2x-DGX-Sparks-TensorFold) serves GLM-5.3-Flash from two DGX Sparks (GB10, 128 GB each). It has two precision knobs. `DENSE` sets the dense weights: `q4` (the default), `fp8` or `bf16`. `KV` sets the KV cache: `fp8` (the default) or `bf16`.

I use this server as the backend for a coding agent. On 2026-10-03 I ran a small comparison to see which settings hold up in long agent sessions.

## The test

The agent was opencode, talking to the server's OpenAI-compatible API. The task was a long, multi-step code-debugging job: diagnose a real CUDA abort in a llama.cpp fork that appears at exactly 2^18 tokens of KV depth. The agent cannot run anything. It gets a read-only checkout and a list of measured symptoms. The symptoms do not all agree with each other. To solve it, the agent has to read the code closely enough to find the contradiction in the symptom data and work out which facts to trust. Each configuration got the same brief. Each ran once, at temperature 1.0. A first fp8-dense attempt was discarded after it read another run's logs.

I judged whether the agent reached the correct conclusion, how many steps it took, and whether its reasoning degenerated after opencode compacted the context. For degeneration I tracked the density of bold markup per 1,000 characters across the session.

All three runs used the same opencode settings: `limit.context` 196,608 and a 65,536-token output limit.

## Results

**`DENSE=q4`, `KV=fp8` (the default).** The agent did not reach the conclusion. It left the last open question unresolved and proposed another experiment. The session compacted twice. After the second compaction the bold-markup density rose from at most 11 to between 18 and 46 per 1,000 characters. The run took 66 steps and 67m56s.

**`DENSE=q4`, `KV=bf16`.** The agent reached the correct conclusion and wrote a full report. The signal never went above 8 over 71 steps. The run took 51m53s.

**`DENSE=fp8`, `KV=fp8`.** The agent found the main cause but left one loose end, with a proposed test to settle it. I scored that as a partial result. It finished in 27 steps and 42m31s, with one compaction. It was the fastest run; its signal peaked at 6 against 8 for `KV=bf16`.

In these runs the default pair did worst, and changing either setting did better.

An earlier run on the default pair, with a larger opencode window, showed the same pattern. It was clean below about 135K tokens of context and degenerated past about 147K. In the default-pair run above, the drift appeared at only 45-88K tokens, after the second compaction. Context length alone does not explain it. My current guess is that fp8 KV adds drift across compactions. The fp8-dense run compacted only once, so it does not test that.

This may be related to a known issue. The recipe's README documents that `q4` can lose the end of turn on short French coding prompts, with replies running to `max_tokens` ([issue #18](https://github.com/MiaAI-Lab/GLM-5.3-Flash-EXL3-2x-DGX-Sparks-TensorFold/issues/18)). `fp8` keeps it.

## Trade-offs

`DENSE=fp8` costs decode speed. The README puts it at about 10%. In its patch table fp8 decodes 38.9 tok/s against q4's 44.4 on prose, and 44.2 against 48.7 on code: 9-12% slower. It does keep the full 1,048,576-token window with the fp8 KV cache.

`KV=bf16` is the exact cache, but it shortens the window a lot:

- `KV=bf16`: 196,608 tokens.
- `KV=bf16` with `VISION=1` and `DENSE=fp8` or `bf16`: 163,840 tokens.
- `KV=bf16 DRAFTER=mtp`: 524,288 tokens, one request at a time.

A restart to change settings took about 2.5 minutes on my pair (142 s until the API answered). The README says later starts take 2 to 6 minutes.

## Recommended setting

For agent work I use fp8 dense weights with the default fp8 KV cache:

```bash
DENSE=fp8 ./start.sh restart
```

To make it stick, put `DENSE=fp8` in `scripts/local.sh` or in a `.env` file next to `start.sh`. The README's order is: environment, then `scripts/local.sh`, then `.env`, then the default.

If you want the exact cache and can live with the shorter window:

```bash
KV=bf16 ./start.sh restart
```

Or, with one request at a time and a longer window:

```bash
KV=bf16 DRAFTER=mtp ./start.sh restart
```

## Matching opencode to the window

opencode needs to know the window, or it compacts at the wrong point. Set `limit.context` to the server's window. opencode also caps output at 32,000 tokens unless you raise it with an environment variable, and `limit.output` alone can only lower that cap. A 64K output needs both:

```bash
export OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=65536
```

And in `opencode.json`, under your provider's model entry (the server's model name is `GLM-5.3-Flash-EXL3`, port 8888):

```json
"GLM-5.3-Flash-EXL3": {
  "limit": { "context": 196608, "output": 65536 }
}
```

Compaction fires at about the window minus the output reserve. With 196,608 and 65,536 it fired at about 129-132K. A bigger `limit.output` lowers the compaction point.

Per configuration:

- `KV=bf16`: `"context": 196608`.
- `KV=bf16` with fp8 or bf16 dense and vision on: `"context": 163840`.
- `KV=bf16 DRAFTER=mtp`: `"context": 524288`.
- `KV=fp8` (any `DENSE`): the server allows 1,048,576. My runs used 196,608 here too, so I have not tested agent behaviour above that.

## Caveat

Each configuration ran once, at temperature 1.0. A second sampled run could change the ordering. I would like repeated runs before calling fp8 KV the cause. I run `DENSE=fp8` until then.
