---
parents:
  - "[[code snippet]]"
  - "[[Lovelace]]"
tags:
  - growing
date: 2025-09-18T10:12:00
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000007
created: 2025-09-18T10:12:00
---

A [[code snippet]] for array jobs on [[Lovelace]].

## Array with a throttle

One task per input file, at most 10 running at once:

```bash
#SBATCH -A LAB_batch_ops
#SBATCH --array=0-99%10
#SBATCH --mem=8G

FILES=(inputs/*.tsv)
srun process "${FILES[$SLURM_ARRAY_TASK_ID]}"
```

The `%10` throttle is the polite part — the scheduler admins notice when you skip it.
