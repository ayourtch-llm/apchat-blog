# Scripts and results for "Removing a loop direction from a small model's weights"

These are the scripts behind the post, as they ran, with three kinds of edit for publication:
four comment lines (run-32k.sh, stage3.sh, stage4.sh, sweep.sh) lost references to our chat,
provenance.sh no longer prints the machine's hostname, and PROVENANCE.md has its hostname and
one home-directory path removed. Nothing that computes a result was changed. The sha256 hashes
in PROVENANCE.md are those of the original files, so those five scripts hash differently here.

- [collect.py](collect.py): base model answers MATH train problems (40 per subject) via llama-server.
- [acts.py](acts.py): finds where each answer starts looping and averages the residual stream before and inside the loop.
- [rank.py](rank.py): prints, per layer, how much the MLP output points along the loop direction.
- [edit.py](edit.py) (edit A) and [edit2.py](edit2.py) (edit B and the sw-* variants): the down_proj column edit.
- [evalmath.py](evalmath.py): MATH-500 evaluation (math_verify), one record per problem.
- [run-editB.sh](run-editB.sh), [run-ref-p50c.sh](run-ref-p50c.sh), [run-32k.sh](run-32k.sh), [sweep.sh](sweep.sh), [stage3.sh](stage3.sh), [stage4.sh](stage4.sh): the runs, in the order they happened.
- [provenance.sh](provenance.sh) and [PROVENANCE.md](PROVENANCE.md): software versions, file hashes, and every run's summary line.
- [base-h400-32k.jsonl](base-h400-32k.jsonl), [editB-h400-32k.jsonl](editB-h400-32k.jsonl), [ref-p50c-h400-32k.jsonl](ref-p50c-h400-32k.jsonl), [sw-a4k256-h400-32k.jsonl](sw-a4k256-h400-32k.jsonl): per-problem results on MATH-500 problems 100-499 (base, our edit B,
  Astra's edit rebuilt as ref-p50c, and the sw-a4k256 variant). Pair them by "idx".

Astra's reference edit is not copied here. It comes from
https://github.com/RikiyaT/lm_understand-logs at commit 4d09ba6d6a7e891dd8063974dfe81b3d78e3494f
(folder exp8_math; run-ref-p50c.sh expects its code in ref/code and the p50c run in ref/runs).
