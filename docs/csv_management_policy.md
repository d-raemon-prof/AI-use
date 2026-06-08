# CSV Master, Backup, and History Policy

## Purpose

Future number-theory observation CSV files should reuse the same base data while preserving a clear history when columns, specifications, or corrections change.

The main lesson is simple: there must be exactly one active master CSV. Generated ZIPs, old CSVs, and nested artifacts must not obscure which file is authoritative.

## Core Rule

Always keep one master CSV as the reference file.

Recommended path:

```text
data/base/clean_sieve_difference_master.csv
```

Project-specific master names are acceptable when useful:

```text
data/base/clean_sieve_difference_M3_to_M420_master.csv
```

All analysis, summaries, visualizations, and derived CSV files must be based on this master CSV.

## No Nested ZIPs

Do not put old ZIP files inside new ZIP files.

Forbidden patterns:

```text
ZIP containing a previous ZIP
old artifact ZIPs repacked into a new artifact ZIP
multiple ambiguously named latest CSV files side by side
```

A ZIP should contain only current deliverables, such as:

```text
master CSV or derived CSV
summary.md
version_history.md
scripts/ when needed
```

## Data Extension vs Schema or Specification Change

### Data Extension Only

This means the target range grows, but the column structure and calculation specification do not change.

Examples:

```text
M=3..420 expanded to M=3..1000
same columns, more rows
same specification recalculated
summary regenerated only
```

In this case, the master CSV may be overwritten.

The summary must state:

```text
data range expanded
no column structure change
master CSV overwritten
```

A backup is optional, but allowed for safety.

### Schema, Specification, or Correction Change

This includes any column addition, deletion, rename, calculation change, classification-condition change, or bug fix.

Examples:

```text
add a new column
rename a column
change route_class logic
change M_reduced_type classification
change gcd or nearest-N rules
fix a wrong previous calculation
```

In this case, a backup is mandatory before overwriting the master CSV.

## Backup Rules

Backup directory:

```text
data/backups/
```

Backup names should include a version or timestamp and reason:

```text
data/backups/clean_sieve_difference_master_v001_before_column_add.csv
data/backups/clean_sieve_difference_master_v002_before_route_fix.csv
data/backups/clean_sieve_difference_master_20260609_1530_before_schema_change.csv
```

At minimum, back up these files when present:

```text
previous master CSV
previous summary.md
previous version_history.md
```

## Version History

Maintain a version history file:

```text
version_history.md
```

or, for a data-specific history:

```text
data/base/version_history.md
```

Every change must append an entry.

Template:

```markdown
## v001 - 2026-06-09

### Type
Initial creation / Data extension / Column addition / Column correction / Bug fix / Classification-condition change

### Target Files
- clean_sieve_difference_master.csv
- clean_sieve_difference_summary.md

### Changes
- Created first table for M=3..420
- Base N values: 2, 6, 30, 210, 2310
- Tied nearest N values output as multiple rows

### Column Changes
- None; initial version

### Calculation Specification Changes
- None; initial version

### Backup
- None

### Notes
- `M_reduced_type=prime` means M_reduced is prime. It does not mean M itself is prime.
```

## When Overwrite Is Allowed

The master CSV may be overwritten when:

```text
column structure is unchanged
calculation specification is unchanged
only the M range is expanded
the same calculation is rerun to fill missing rows
summary.md only is regenerated
```

Still append a light history entry.

Example:

```markdown
## v002 - 2026-06-09

### Type
Data extension

### Changes
- Expanded target range from M=3..420 to M=3..1000
- No column structure change
- No calculation specification change

### Backup
- None
```

## Mandatory Backup Cases

Always back up first when:

```text
adding columns
removing columns
renaming columns
changing classification conditions such as route_class
changing formulas
changing base-N selection
changing tied-nearest-N handling
fixing a miscalculation
breaking compatibility with the previous master CSV
```

## Recommended Directory Layout

```text
project_root/
  README.md
  version_history.md

  data/
    base/
      clean_sieve_difference_master.csv
      clean_sieve_difference_summary.md

    backups/
      clean_sieve_difference_master_v001_before_schema_change.csv
      clean_sieve_difference_summary_v001_before_schema_change.md

    derived/
      filtered_pm1_reduction.csv
      filtered_prime_power.csv
      route_class_counts.csv

  scripts/
    clean_sieve_difference.py
    summarize_clean_sieve_difference.py

  outputs/
    clean_sieve_difference_current.zip
```

## Master CSV vs Derived CSV

Master CSV:

```text
data/base/clean_sieve_difference_master.csv
```

Derived CSV files go under:

```text
data/derived/
```

Examples:

```text
data/derived/pm1_reduction_only.csv
data/derived/full_off_new_only.csv
data/derived/prime_power_reduced_only.csv
```

Derived CSV files must never replace the master CSV.

## ZIP Output Rule

Use a stable current ZIP name when possible:

```text
outputs/clean_sieve_difference_current.zip
```

Recommended contents:

```text
data/base/clean_sieve_difference_master.csv
data/base/clean_sieve_difference_summary.md
version_history.md
optional data/derived/*.csv
optional scripts/*.py
```

Never put old ZIPs inside the new ZIP.

## Codex Pre-Run Check

Before processing, Codex must state:

```text
Processing type:
  Initial creation / Data extension / Schema change / Correction / Derived aggregation

Master CSV:
  data/base/clean_sieve_difference_master.csv

Column structure change:
  yes / no

Calculation specification change:
  yes / no

Backup creation:
  required / not required

version_history.md update:
  yes
```

## Codex Post-Run Check

After processing, Codex must include the following in the summary:

```text
master CSV row count
target M range
column count
column names
route_class counts
pm1_reduction_type counts
M_reduced_type counts
M values with multiple tied nearest-N rows
whether backups were created
version_history entry summary
```

## Standard Prompt Prefix

Use this at the start of future data-processing prompts when possible:

```text
Manage the master CSV as exactly one file: data/base/clean_sieve_difference_master.csv.
For data extensions without column or calculation-specification changes, overwrite the master CSV.
For column additions, column renames, calculation-specification changes, classification-condition changes, or corrections, first back up the previous CSV under data/backups/ and append the reason, changes, and backup names to version_history.md.
Do not nest old ZIP files inside new ZIP files.
Place derived CSV files under data/derived/ and never use them to replace the master CSV.
```

## One-Line Summary

Keep exactly one active master CSV. Back up and append history only when the schema, specification, classification logic, or previous calculation changes; simple data extension may overwrite the master CSV.
