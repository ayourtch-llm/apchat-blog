#!/usr/bin/env python3
"""Score a llama-server model on MATH-500 problems with Qwen3.5-0.8B's thinking-mode sampling.
usage: evalmath.py PORT OUT.jsonl N_PROBLEMS SAMPLES [MAX_TOKENS]
env OFFSET=K: score problems K..K+N-1 instead of 0..N-1 (idx and seeds stay absolute, so runs are comparable).
Records per sample: problem idx, finish_reason (length = hit the cap), completion tokens, correct."""
import asyncio, json, sys, aiohttp
from math_verify import parse, verify
port, out, n, k = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
maxtok = int(sys.argv[5]) if len(sys.argv) > 5 else 32768
OFF = int(__import__("os").environ.get("OFFSET", "0"))
probs = [json.loads(l) for l in open("data-math500.jsonl")]
PROMPT = "{}\nPlease reason step by step, and put your final answer within \\boxed{{}}."
sem = asyncio.Semaphore(16)
async def one(s, i, j, f):
    p = probs[i]
    body = {"messages": [{"role": "user", "content": PROMPT.format(p["problem"])}],
            "temperature": 0.6, "top_p": 0.95, "top_k": 20, "presence_penalty": 1.5,
            "max_tokens": maxtok, "seed": 1000 * i + j,
            "chat_template_kwargs": {"enable_thinking": True}}
    async with sem:
        for attempt in range(3):
            try:
                async with s.post(f"http://127.0.0.1:{port}/v1/chat/completions", json=body,
                                  timeout=aiohttp.ClientTimeout(total=7200)) as r:
                    d = await r.json()
                break
            except Exception as e:
                print(f"ERR idx={i} s={j} attempt={attempt}: {type(e).__name__}: {e}", file=sys.stderr)
                d = None
    if d is None or "choices" not in d:
        print(f"ERR idx={i} s={j} bad response: {str(d)[:300]}", file=sys.stderr); return
    c = d["choices"][0]; txt = c["message"].get("content") or ""
    try:
        ok = bool(verify(parse("$" + p["answer"] + "$"), parse(txt)))
    except Exception as e:
        print(f"ERR verify idx={i}: {e}", file=sys.stderr); ok = False
    rec = {"idx": i, "s": j, "finish": c.get("finish_reason"), "tokens": d["usage"]["completion_tokens"], "correct": ok}
    f.write(json.dumps(rec) + "\n"); f.flush()
async def main():
    with open(out, "w") as f:
        async with aiohttp.ClientSession() as s:
            await asyncio.gather(*[one(s, i, j, f) for i in range(OFF, OFF + n) for j in range(k)])
    rs = [json.loads(l) for l in open(out)]
    N = len(rs)
    print(f"{out}: n={N} acc={100*sum(r['correct'] for r in rs)/N:.1f}% hit_limit={100*sum(r['finish']=='length' for r in rs)/N:.1f}% mean_tokens={sum(r['tokens'] for r in rs)/N:.0f}")
asyncio.run(main())
