# delta-doctor

**Stop guessing why your Delta table won't write. Diagnose protocol-level issues in one command.**

[![PyPI](https://img.shields.io/pypi/v/delta-doctor.svg)](https://pypi.org/project/delta-doctor/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Delta Lake tables break in ways that produce cryptic errors and silent data corruption. `delta-doctor` reads your table's `_delta_log`, checks protocol invariants, and tells you exactly what's wrong and how to fix it.

---

## The Problem

You try to write to a Delta table and get:

```
io.delta.exceptions.DeltaProtocolVersionException:
  Requirement failed: The protocol version of your Delta table is incompatible
  with the version of Delta Lake you are using.
```

No table name. No offending feature. No suggested fix. Just hours of digging through `_delta_log/*.json` by hand.

## The Fix

```bash
$ delta-doctor diagnose /path/to/table

delta-doctor v0.2.1
Table: /path/to/table
Protocol: reader=3 writer=7
────────────────────────────────────────────────
✗ FAIL  writer_features contains "appendOnly" but no
        delta.appendOnly table property is set.
        → Remove "appendOnly" from writer_features, or
          ALTER TABLE ... SET TBLPROPERTIES ('delta.appendOnly' = 'true')

✗ FAIL  invariants writer feature enabled, but no
        delta.invariants table property is set.
        → Either add invariant expressions via
          ALTER TABLE ... SET TBLPROPERTIES ('delta.invariants' = '[...]')
          or remove "invariants" from writer_features.

✓ PASS  reader_version 3 is supported by current clients
✓ PASS  checkpoint schema matches protocol
────────────────────────────────────────────────
2 issues found. Run `delta-doctor fix --dry-run` to preview fixes.
```

One command. Clear diagnosis. Actionable fixes.

---

## Before / After

**Without delta-doctor** — a wall of opaque error, no context:

```
$ spark.sql("INSERT INTO my_table VALUES (1, 'a')")
...
DeltaProtocolVersionException: (java.lang.IllegalStateException) The protocol
version of your Delta table is incompatible with the version of Delta Lake
you are using.
  at io.delta.standalone.internal.DeltaShared...
  at io.delta.standalone.internal.DeltaLogImpl...
  (47 more lines of Java stack trace)
```

**With delta-doctor** — the actual cause and the fix:

```
$ delta-doctor diagnose /data/my_table
✗ FAIL  writer_features contains "appendOnly" but no
        delta.appendOnly table property is set.
        → Remove "appendOnly" from writer_features, or
          ALTER TABLE ... SET TBLPROPERTIES ('delta.appendOnly' = 'true')
```

---

## Install

```bash
pip install delta-doctor
```

Or from source:

```bash
git clone https://github.com/Tabish0007/delta-doctor.git
cd delta-doctor
pip install -e .
```

Requires Python 3.9+. Works with Delta Lake tables on local filesystem, S3, GCS, and Azure Blob Storage.

---

## Usage

```bash
# Diagnose a table
delta-doctor diagnose /path/to/table

# Diagnose with verbose output (shows passing checks too)
delta-doctor diagnose /path/to/table --verbose

# Preview fixes without applying
delta-doctor fix /path/to/table --dry-run

# Apply fixes (rewrites _delta_log protocol entry)
delta-doctor fix /path/to/table --yes

# Check all tables under a path
delta-doctor scan /warehouse/ --recursive
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Table is healthy |
| 1 | Issues found |
| 2 | Table unreadable / not a Delta table |

Use these in CI: `delta-doctor scan $WAREHOUSE --recursive` will fail the build on unhealthy tables.

---

## What It Checks

- **Protocol invariants** — writer features that require matching table properties (`appendOnly`, `invariants`, `changeDataFeed`, `generatedColumns`, `columnMapping`)
- **Reader/writer version compatibility** — flags features that older clients in your fleet can't read
- **Checkpoint integrity** — schema drift between Parquet checkpoints and JSON commits
- **Orphaned log entries** — commits that reference removed files, or files with no commit
- **Table property consistency** — `delta.minReaderVersion` / `delta.minWriterVersion` vs. actual protocol fields

---

## Use in CI

```yaml
# .github/workflows/delta-health.yml
- name: Check Delta tables
  run: |
    pip install delta-doctor
    delta-doctor scan s3://my-bucket/warehouse --recursive
```

Fails the workflow if any table has protocol-level issues — catches corruption before it hits production queries.

---

## Roadmap

- [ ] `cargo` build for a standalone static binary (no Python runtime)
- [ ] JSON / SARIF output for CI integrations
- [ ] Repair mode for missing checkpoint files
- [ ] Support for Delta Lake 4.0 protocol features

---

## Contributing

Issues and PRs welcome. If you've hit a Delta protocol error that `delta-doctor` didn't diagnose well, please [open an issue](https://github.com/Tabish0007/delta-doctor/issues) with the `_delta_log/00000000000000000000.json` protocol entry (redact paths).

---

## License

MIT

---

*If this saved you time, a ⭐ helps others find it.*
