# AI-use

Python scripts for experimental ABC-quality and sieve-style number-theory searches.

## Codex Compute Policy

Codex should follow `AGENTS.md` before running nontrivial searches in this repository. In short: use the repo environment, bound every search, do a small smoke test first, estimate load, and stop before a heavy server-side run if the cost looks risky. Heavy scans should be prepared as reproducible local commands instead of being forced through a thin or shared runtime.

## CSV Management Policy

For observation CSV work, use exactly one master CSV and follow `docs/csv_management_policy.md`. Simple data extension may overwrite the master CSV when columns and calculation rules are unchanged. Schema changes, classification-rule changes, calculation changes, or corrections require backups under `data/backups/` and a `version_history.md` entry. Old ZIP files must not be nested inside new ZIP files.

## ABC Quality Candidate Search

This repository currently contains `search.py`, which searches candidates of the form:

```text
a + p^e * P = q^k
```

with the initial ranges:

```text
a in [1, 2, 3, 5, 7, 11, 13, 17, 19]
p in [2, 3, 5, 7, 11]
e in [2, 40]
k in [2, 20]
q in [2, Q_MAX]
```

`q` is bounded by `Q_MAX` because the prompt ranges do not otherwise make the search finite. The default is `Q_MAX = 30`, which is enough to detect the known example:

```text
2 + 3^10 * 109 = 23^5
```

You can increase the bound with `--q-max`.

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

On macOS/Linux, use:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
python search.py
```

or with a wider `q` search:

```bash
python search.py --q-max 100
```

The script writes:

```text
outputs/abc_quality_candidates.csv
results.md
```

For each candidate it computes:

- `a,b,c`
- `p,e,P,q,k`
- factorization of `P`
- `rad(abc)`
- ABC quality `Q = log(c) / log(rad(abc))`
- `Dp_b = e*log(p)/log(b)`
- maximum prime factor of `P`
- whether `P` is prime
- boundary ratio `T = Ec/(2*Bab + log(rad(c)))`
- `Ec = log(c) - log(rad(c))`
- `Bab = log(rad(a)) + log(rad(b))`

## Local Fallback

`sympy` is the intended factorization engine. A lightweight Miller-Rabin + Pollard Rho fallback is included so the script can still run in constrained environments, but larger searches should use `sympy`.
