#!/usr/bin/env python3
"""Generate thinking-mode answers on MATH TRAIN problems (never the test set) and keep the text,
so loop onsets can be found. usage: collect.py PORT OUT.jsonl N MAX_TOKENS"""
import asyncio, json, sys, aiohttp
from datasets import load_dataset
port, out, n, maxtok = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
subs = ["algebra", "counting_and_probability", "geometry", "intermediate_algebra", "number_theory", "prealgebra", "precalculus"]
probs = []
for s in subs:
    probs += [r["problem"] for r in load_dataset("EleutherAI/hendrycks_math", s, split="train").select(range(40))]
probs = probs[:n]
PROMPT = "{}\nPlease reason step by step, and put your final answer within \\boxed{{}}."
sem = asyncio.Semaphore(16)
async def one(s, i, f):
    body = {"messages": [{"role": "user", "content": PROMPT.format(probs[i])}],
            "temperature": 0.6, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5,
            "max_tokens": maxtok, "seed": 7 + i, "chat_template_kwargs": {"enable_thinking": True}}
    async with sem:
        try:
            async with s.post(f"http://127.0.0.1:{port}/v1/chat/completions", json=body,
                              timeout=aiohttp.ClientTimeout(total=3600)) as r:
                d = await r.json()
        except Exception as e:
            print(f"ERR idx={i}: {type(e).__name__}: {e}", file=sys.stderr); return
    if "choices" not in d:
        print(f"ERR idx={i} bad response: {str(d)[:300]}", file=sys.stderr); return
    m = d["choices"][0]["message"]
    f.write(json.dumps({"idx": i, "prompt": PROMPT.format(probs[i]), "reasoning": m.get("reasoning_content") or "",
                        "content": m.get("content") or "", "finish": d["choices"][0]["finish_reason"],
                        "tokens": d["usage"]["completion_tokens"]}) + "\n"); f.flush()
async def main():
    with open(out, "w") as f:
        async with aiohttp.ClientSession() as s:
            await asyncio.gather(*[one(s, i, f) for i in range(len(probs))])
asyncio.run(main())
