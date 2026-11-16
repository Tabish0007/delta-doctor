# delta-doctor

A CLI tool to diagnose and fix Delta Lake table health issues.

## What it does

- **Protocol Health**: Detects unused writer features (`appendOnly`, `invariants`) that break reader compatibility
- **Performance Health**: Flags small files that slow down queries
- **Fix**: Removes unused protocol features directly from the Delta log

## Install

```bash
pip install -e .

