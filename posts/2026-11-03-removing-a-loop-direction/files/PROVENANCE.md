# wsp-loop provenance (generated 2026-11-03T21:49:53Z by provenance.sh on the GPU machine)

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

## Software
- llama.cpp: 9ce18eac06c16a53fb4850594ac2fea04bbf9409 Wed Aug 26 06:38:07 2026 +0000
- python venv: Python 3.12.3; 
- GPU: 2, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 610.57.04

## File hashes (sha256)
```
693897b38e938c69268b58e8a23811912fa0e16c9b684d28c9e812fb0db126ed  gguf/base.gguf
ab610694baef7ac2de059e0ac1cbb69bbcafe9bcfedc3c738b1d35eb8f264fed  gguf/edit-A.gguf
0022bbf2db8753006e49a62d1a9b6a6d188b6ace8c866c1bdc2994004def5aa6  gguf/editB.gguf
e2d07ccc1a6b48e86f25b1de2fb7861b885dd2b8768e32e10c676f016ac9fd4c  gguf/ref-p50c.gguf
aab3a0cdddce63e7b3271a579e125e345cb42dedbc196690f73003eca50812b1  gguf/sw-a12k64.gguf
7cb4c73b5110104f52374444d6f604d13506943c4a939d306d9644eaa820215c  gguf/sw-a3k64L13-21.gguf
7d0732bfaf1476cf52d589ee645e3a36e3e65c0de4a77c4555207da009b8a264  gguf/sw-a4k256.gguf
d079de568416df7d0b9f0544ce5e85daea06a725fa9182d5642a2700f646f491  gguf/sw-a4k64.gguf
017d2382f2a13abec83376e0688fab3596fa8dc7b6e7f687bf3b937999e99714  gguf/sw-a6k256.gguf
fb4abea461bbd28ea8f085b0168a7db420c3a2dfa0b0b89be8701f8cee09a494  gguf/sw-a6k64L13-21.gguf
6b05fd7cba2ba43e9da3ec8e0ebfd4446f56c8a3e3115bfc452d233ed7b758ea  gguf/sw-a8k256.gguf
d8084eedca0ea0ec943889d1a005e57cb978ca702b9b14b1c2a27a4c4010a4c6  gguf/sw-a8k64.gguf
40c413fe845928b32df28926a6e4c6317fdc909334ca8224fa674f5f1e24b6ba  acts.py
0421f363669af2ce921eadac1903c937fba3f43fb3864aa900ef450aed28503b  collect.py
ad5e53968cfed3b9654dfe5b5d53c27424355ca18c3b362e8de8e775e733324c  edit2.py
25fd13e2638315042f0a3cfb3ad506eed28a5f3bd866aca47527a4cb86cd1b4f  edit.py
07c9c7a7af6eadcfbd58eb06a328ae03becbc72455285bb34d6f332cc248cfce  evalmath.py
6c6d6af3e593105a9cdbfbe205a4382a16d410f30ef19c035b4c29f5daf1f9d4  rank.py
d2b627a6cf344f309cca4bcab4ff6ccc6ad1c8f29cabda78d11f99c19d1b1c5d  ref/code/apply_edit.py
da0759bd0a150392b7aaa330f9d242429f47b49c0f900d0d890c91832c9217db  ref/code/build_ckpt.py
c93f477c02b3ae0d6b37abe3afad8bb7353e273322ff963eec7ff2270012035d  ref/code/evaluate.py
2bf84b497e308e07be94d969d6763cd8396de44cb0aaf5213a6b1075999287a1  ref/code/make_edit_diff.py
f0d576a1adc625dede7bff749b3bf8c9a5a8f6bae43d51e2d0ee36d694e89843  ref/code/mathqa.py
2ecd0420c929f721f547b8f189cf0a24343d960ed3b0e9b2892d9c7c8cede021  ref/code/merge.py
6e19a615fd04d20af7641900c32198010a716939b91f926c7fe2c1cc781f99db  ref/code/practice35.py
ba4be365e44c3e165b9c3982af9dbcd8ec94f7fd0430e5fd9de1d57f249a4ae4  ref/code/profiles.py
3c4e532fb8edf374e1a4636aa806a04d062f824943eaf4bca0d3af5b0e7dca40  ref/code/st_numpy.py
9f91365cf2d643827ba44b6df001d8792903f323bbc0d14039b4b79389a0d869  provenance.sh
8738bec4be42174aa6162bf370f3a49fe1279f4c8c63b7ff5763cec7054dbe5c  run-32k.sh
fdac4a21939f5649dcec7ba74757a041b38a488198f73f91a18baa2d1e825a7f  run-editB.sh
43acd58435e6921ba8066d3460b7d19617ee9ce2622fcf1380f13d75aab1d8a7  run-ref-p50c.sh
4c81efe2e300f378406d80ab9adf718121ca829563e863f33313143062b297e8  stage3.sh
5124b900aa6ea1436a06960d906c9922643c2fed9bdd2da1ce4f9cb115db6dda  stage4.sh
17ece45846e6fb4297f068e31006635120a9660fe664f0a9744e4ce06c1c230d  sweep.sh
c77900ce98be04b5c6c342f32f2cb5037607cd7bf2490ceba1edce7a90bf5269  sweep-jobs.txt
200806fb17234213e909649c09a14ce01ef836b32d3bcb1a261fcf96cda4470f  data-math500.jsonl
80b5e3c29c74573c7ac7b51ffcf7a70135334be839a6a9edbd0e1a8349d1cb4f  collect-train-8k.jsonl
96484919ca7b1d4a67cc4fe12abdfdd6a7f8799f3aaea4e74af61e22d3a2ee9f  acts-250.pt
173c87a53759e0201f33e0ccf978e510c2042d7f2cb78229d9a50d79b9e7dd08  ~/models/wiki.test.raw
04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696  models/Qwen3.5-0.8B/model.safetensors-00001-of-00001.safetensors
```

## Edit build logs (first lines)
- build-sw-a12k64.log: layer 15: 64 columns, alpha 12.0, overlap with p50c columns 29/64;layer 19: 64 columns, alpha 12.0, overlap with p50c columns 19/64;
- build-sw-a3k64L13-21.log: layer 13: 64 columns, alpha 3.0, overlap with p50c columns 0/64;layer 14: 64 columns, alpha 3.0, overlap with p50c columns 0/64;layer 15: 64 columns, alpha 3.0, overlap with p50c columns 29/64;layer 16: 64 columns, alpha 3.0, overlap with p50c columns 0/64;layer 17: 64 columns, alpha 3.0, overlap with p50c columns 0/64;layer 18: 64 columns, alpha 3.0, overlap with p50c columns 0/64;layer 19: 64 columns, alpha 3.0, overlap with p50c columns 19/64;layer 20: 64 columns, alpha 3.0, overlap with p50c columns 0/64;layer 21: 64 columns, alpha 3.0, overlap with p50c columns 0/64;
- build-sw-a4k256.log: layer 15: 256 columns, alpha 4.0, overlap with p50c columns 40/256;layer 19: 256 columns, alpha 4.0, overlap with p50c columns 36/256;
- build-sw-a4k64.log: layer 15: 64 columns, alpha 4.0, overlap with p50c columns 29/64;layer 19: 64 columns, alpha 4.0, overlap with p50c columns 19/64;
- build-sw-a6k256.log: layer 15: 256 columns, alpha 6.0, overlap with p50c columns 40/256;layer 19: 256 columns, alpha 6.0, overlap with p50c columns 36/256;
- build-sw-a6k64L13-21.log: layer 13: 64 columns, alpha 6.0, overlap with p50c columns 0/64;layer 14: 64 columns, alpha 6.0, overlap with p50c columns 0/64;layer 15: 64 columns, alpha 6.0, overlap with p50c columns 29/64;layer 16: 64 columns, alpha 6.0, overlap with p50c columns 0/64;layer 17: 64 columns, alpha 6.0, overlap with p50c columns 0/64;layer 18: 64 columns, alpha 6.0, overlap with p50c columns 0/64;layer 19: 64 columns, alpha 6.0, overlap with p50c columns 19/64;layer 20: 64 columns, alpha 6.0, overlap with p50c columns 0/64;layer 21: 64 columns, alpha 6.0, overlap with p50c columns 0/64;
- build-sw-a8k256.log: layer 15: 256 columns, alpha 8.0, overlap with p50c columns 40/256;layer 19: 256 columns, alpha 8.0, overlap with p50c columns 36/256;
- build-sw-a8k64.log: layer 15: 64 columns, alpha 8.0, overlap with p50c columns 29/64;layer 19: 64 columns, alpha 8.0, overlap with p50c columns 19/64;

## Runs (one line per result file: summary line from its .log)
```
base-h400-32k.log :: base-h400-32k.jsonl: n=400 acc=7.0% hit_limit=93.0% mean_tokens=30963 :: ERR-lines=0
base-m100x1-16k.log :: base-m100x1-16k.jsonl: n=100 acc=11.0% hit_limit=89.0% mean_tokens=15503 :: ERR-lines=0
base-m100x1-32k.log :: base-m100x1-32k.jsonl: n=100 acc=6.0% hit_limit=94.0% mean_tokens=31480 :: ERR-lines=0
base-m100x2.log ::  :: ERR-lines=0
editA-m100x1-16k.log :: editA-m100x1-16k.jsonl: n=100 acc=6.0% hit_limit=94.0% mean_tokens=15841 :: ERR-lines=0
editB-h400-32k.log :: editB-h400-32k.jsonl: n=400 acc=25.2% hit_limit=75.0% mean_tokens=28997 :: ERR-lines=0
editB-m100x1-16k.log :: editB-m100x1-16k.jsonl: n=100 acc=17.0% hit_limit=83.0% mean_tokens=15315 :: ERR-lines=0
editB-m100x1-32k.log :: editB-m100x1-32k.jsonl: n=100 acc=29.0% hit_limit=74.0% mean_tokens=28276 :: ERR-lines=0
ref-p50c-h400-32k.log :: ref-p50c-h400-32k.jsonl: n=400 acc=27.5% hit_limit=66.0% mean_tokens=27702 :: ERR-lines=0
ref-p50c-m100x1-16k.log :: ref-p50c-m100x1-16k.jsonl: n=100 acc=18.0% hit_limit=82.0% mean_tokens=15132 :: ERR-lines=0
ref-p50c-m100x1-32k.log :: ref-p50c-m100x1-32k.jsonl: n=100 acc=28.0% hit_limit=65.0% mean_tokens=27104 :: ERR-lines=0
sw-a12k64-m100x1-16k.log :: sw-a12k64-m100x1-16k.jsonl: n=100 acc=8.0% hit_limit=94.0% mean_tokens=15928 :: ERR-lines=0
sw-a3k64L13-21-m100x1-16k.log :: sw-a3k64L13-21-m100x1-16k.jsonl: n=100 acc=10.0% hit_limit=90.0% mean_tokens=15793 :: ERR-lines=0
sw-a4k256-h400-32k.log :: sw-a4k256-h400-32k.jsonl: n=400 acc=21.0% hit_limit=80.5% mean_tokens=29251 :: ERR-lines=0
sw-a4k256-m100x1-16k.log :: sw-a4k256-m100x1-16k.jsonl: n=100 acc=13.0% hit_limit=87.0% mean_tokens=15749 :: ERR-lines=0
sw-a4k256-m100x1-32k.log :: sw-a4k256-m100x1-32k.jsonl: n=100 acc=30.0% hit_limit=74.0% mean_tokens=28391 :: ERR-lines=0
sw-a4k64-m100x1-16k.log :: sw-a4k64-m100x1-16k.jsonl: n=100 acc=11.0% hit_limit=89.0% mean_tokens=15558 :: ERR-lines=0
sw-a4k64-m100x1-32k.log :: sw-a4k64-m100x1-32k.jsonl: n=100 acc=29.0% hit_limit=70.0% mean_tokens=27810 :: ERR-lines=0
sw-a6k256-m100x1-16k.log :: sw-a6k256-m100x1-16k.jsonl: n=100 acc=10.0% hit_limit=90.0% mean_tokens=15645 :: ERR-lines=0
sw-a6k256-m100x1-32k.log :: sw-a6k256-m100x1-32k.jsonl: n=100 acc=27.0% hit_limit=79.0% mean_tokens=29416 :: ERR-lines=0
sw-a6k64L13-21-m100x1-16k.log :: sw-a6k64L13-21-m100x1-16k.jsonl: n=100 acc=5.0% hit_limit=95.0% mean_tokens=15744 :: ERR-lines=0
sw-a8k256-m100x1-16k.log :: sw-a8k256-m100x1-16k.jsonl: n=100 acc=8.0% hit_limit=93.0% mean_tokens=15872 :: ERR-lines=0
sw-a8k64-m100x1-16k.log :: sw-a8k64-m100x1-16k.jsonl: n=100 acc=8.0% hit_limit=92.0% mean_tokens=15765 :: ERR-lines=0
sw-a8k64-m100x1-32k.log :: sw-a8k64-m100x1-32k.jsonl: n=100 acc=25.0% hit_limit=74.0% mean_tokens=28666 :: ERR-lines=0
```

## Perplexity
```
ppl-base.log Final estimate: PPL = 14.6194 +/- 0.17754
ppl-editB.log Final estimate: PPL = 14.9173 +/- 0.17942
ppl-ref-p50c.log Final estimate: PPL = 14.7816 +/- 0.17452
ppl-sw-a4k256.log Final estimate: PPL = 14.7340 +/- 0.17684
ppl-sw-a4k64.log Final estimate: PPL = 14.6417 +/- 0.17614
ppl-sw-a6k256.log Final estimate: PPL = 15.2346 +/- 0.18304
ppl-sw-a8k64.log Final estimate: PPL = 15.4568 +/- 0.18637
```

## Driver outputs (timestamps per job)
### run-32k.out
```
base SERVER PID 2445748
editB SERVER PID 2445749
editB DONE
base DONE
RUN32K-DONE
```
### sweep.out
```
START Tue Nov  3 08:35:01 AM UTC 2026
BUILT Tue Nov  3 08:35:57 AM UTC 2026
DONE sw-a4k64-m100x1-16k sw-a4k64-m100x1-16k.jsonl: n=100 acc=11.0% hit_limit=89.0% mean_tokens=15558
DONE sw-a8k64-m100x1-16k sw-a8k64-m100x1-16k.jsonl: n=100 acc=8.0% hit_limit=92.0% mean_tokens=15765
DONE sw-a12k64-m100x1-16k sw-a12k64-m100x1-16k.jsonl: n=100 acc=8.0% hit_limit=94.0% mean_tokens=15928
DONE ref-p50c-m100x1-32k ref-p50c-m100x1-32k.jsonl: n=100 acc=28.0% hit_limit=65.0% mean_tokens=27104
DONE sw-a6k256-m100x1-16k sw-a6k256-m100x1-16k.jsonl: n=100 acc=10.0% hit_limit=90.0% mean_tokens=15645
DONE sw-a4k256-m100x1-16k sw-a4k256-m100x1-16k.jsonl: n=100 acc=13.0% hit_limit=87.0% mean_tokens=15749
DONE sw-a8k256-m100x1-16k sw-a8k256-m100x1-16k.jsonl: n=100 acc=8.0% hit_limit=93.0% mean_tokens=15872
DONE sw-a6k64L13-21-m100x1-16k sw-a6k64L13-21-m100x1-16k.jsonl: n=100 acc=5.0% hit_limit=95.0% mean_tokens=15744
DONE sw-a3k64L13-21-m100x1-16k sw-a3k64L13-21-m100x1-16k.jsonl: n=100 acc=10.0% hit_limit=90.0% mean_tokens=15793
SWEEP-DONE Tue Nov  3 10:54:36 AM UTC 2026
```
### stage3.out
```
START Tue Nov  3 10:55:07 AM UTC 2026
PPL base Final estimate: PPL = 14.6194 +/- 0.17754
PPL editB Final estimate: PPL = 14.9173 +/- 0.17942
PPL ref-p50c Final estimate: PPL = 14.7816 +/- 0.17452
PPL sw-a4k256 Final estimate: PPL = 14.7340 +/- 0.17684
PPL sw-a8k64 Final estimate: PPL = 15.4568 +/- 0.18637
PPL sw-a6k256 Final estimate: PPL = 15.2346 +/- 0.18304
PPL sw-a4k64 Final estimate: PPL = 14.6417 +/- 0.17614
DONE sw-a4k256-m100x1-32k sw-a4k256-m100x1-32k.jsonl: n=100 acc=30.0% hit_limit=74.0% mean_tokens=28391
DONE sw-a8k64-m100x1-32k sw-a8k64-m100x1-32k.jsonl: n=100 acc=25.0% hit_limit=74.0% mean_tokens=28666
DONE sw-a6k256-m100x1-32k sw-a6k256-m100x1-32k.jsonl: n=100 acc=27.0% hit_limit=79.0% mean_tokens=29416
STAGE3-DONE Tue Nov  3 12:30:02 PM UTC 2026
```
### stage4.out
```
START 2026-11-03T14:06:13Z
BEGIN base-h400-32k 2026-11-03T14:06:13Z gguf=base.gguf cap=32768 n=400 offset=100
BEGIN editB-h400-32k 2026-11-03T14:06:33Z gguf=editB.gguf cap=32768 n=400 offset=100
BEGIN sw-a4k256-h400-32k 2026-11-03T14:06:53Z gguf=sw-a4k256.gguf cap=32768 n=400 offset=100
BEGIN ref-p50c-h400-32k 2026-11-03T14:07:13Z gguf=ref-p50c.gguf cap=32768 n=400 offset=100
DONE ref-p50c-h400-32k 2026-11-03T19:51:57Z ref-p50c-h400-32k.jsonl: n=400 acc=27.5% hit_limit=66.0% mean_tokens=27702
DONE editB-h400-32k 2026-11-03T20:04:12Z editB-h400-32k.jsonl: n=400 acc=25.2% hit_limit=75.0% mean_tokens=28997
DONE sw-a4k256-h400-32k 2026-11-03T20:06:49Z sw-a4k256-h400-32k.jsonl: n=400 acc=21.0% hit_limit=80.5% mean_tokens=29251
DONE base-h400-32k 2026-11-03T20:21:37Z base-h400-32k.jsonl: n=400 acc=7.0% hit_limit=93.0% mean_tokens=30963
BEGIN sw-a4k64-m100x1-32k 2026-11-03T20:21:37Z gguf=sw-a4k64.gguf cap=32768 n=100 offset=0
DONE sw-a4k64-m100x1-32k 2026-11-03T21:41:58Z sw-a4k64-m100x1-32k.jsonl: n=100 acc=29.0% hit_limit=70.0% mean_tokens=27810
STAGE4-DONE 2026-11-03T21:41:58Z
```
