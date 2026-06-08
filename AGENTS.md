# Codex Operating Policy for AI-use

This repository is used for experimental number-theory searches. Some tasks can become computationally expensive very quickly. Codex should treat every nontrivial search as a bounded experiment, not as an open-ended job.

## Default Environment Policy

- Prefer running computations inside this repository's explicit Python environment instead of a projectless Codex thread.
- Use the repository dependency files first, especially `requirements.txt`.
- Do not assume that the ambient `python` command, bundled Codex Python, or globally installed packages are suitable.
- If dependencies are missing, report the missing dependency and propose installing it in the repo environment. Do not silently rewrite the algorithm merely to fit a thin runtime unless the task is explicitly lightweight.

## CSV Master, Backup, and History Policy

For number-theory observation CSV work, Codex must follow `docs/csv_management_policy.md`.

Mandatory short form:

- Keep exactly one active master CSV, normally `data/base/clean_sieve_difference_master.csv`.
- Put derived CSV files under `data/derived/`; never let a derived CSV replace the master CSV.
- Do not nest old ZIP files inside new ZIP files.
- Data extension with unchanged columns and unchanged calculation specification may overwrite the master CSV.
- Column additions, column deletion, column renames, calculation-specification changes, classification-condition changes, base-N rule changes, tie-handling changes, or bug fixes require a backup first under `data/backups/`.
- Every change must append to `version_history.md` or `data/base/version_history.md`.
- Before processing, state the processing type, master CSV path, whether columns change, whether calculation specification changes, whether backup is required, and that version history will be updated.
- After processing, summarize row count, target range, column count and names, key class counts, tied nearest-N rows, backup status, and version-history entry.

## Compute Safety Policy

Before running any potentially expensive search, Codex must do a preflight check.

Preflight checklist:

1. Identify all free search dimensions and their bounds.
2. Estimate the rough candidate count from the Cartesian product of bounds.
3. Identify expensive operations inside the loop, especially factorization, primality tests, gcd-heavy loops, large powers, CSV writes, or repeated symbolic operations.
4. Run a tiny smoke test first, using deliberately small bounds.
5. Record elapsed time for the smoke test when possible.
6. Extrapolate conservatively before increasing bounds.
7. Stop if the extrapolation suggests high server load, long runtime, large memory use, or runaway output size.

If the server-side load looks questionable, Codex should not continue the heavy run. It should summarize why the run is risky and suggest a local execution plan instead.

## Hard Stops

Stop and ask or propose local execution if any of these are true:

- A search dimension is unbounded or only implicitly bounded.
- The candidate space is large and each candidate requires factorization of large integers.
- A smoke test is slow enough that the full run would likely take many minutes or more.
- The output CSV or intermediate data would become very large.
- The environment lacks the intended math libraries and fallback code would be much slower.
- The task would require installing dependencies or using network access in a restricted environment.

## Local-First Escalation

When a run is too heavy for the current Codex/server environment, prefer this path:

1. Keep the algorithm and configuration in the repo.
2. Add or update a script with CLI bounds such as `--q-max`, `--m-end`, `--limit`, or `--sample`.
3. Add a README command for local execution.
4. Add a small verified sample result to `results.md`.
5. Tell the user what command to run locally for the wider scan.

## Results Policy

- Commit source code, configuration, documentation, and small summaries.
- Do not commit large generated CSV files by default.
- Write generated data under `outputs/`, which is ignored by git.
- Include enough summary in `results.md` to verify that known examples are detected.

## ABC Search Notes

For `a + p^e * P = q^k` searches:

- Treat `q` as requiring an explicit bound such as `--q-max`.
- Verify the known example `2 + 3^10 * 109 = 23^5` for small/default runs.
- Be cautious with factorization of large `P`, `b`, or `rad(abc)` values.
- Prefer `sympy.factorint` in the repo environment; fallback factorization is only for small smoke tests.
