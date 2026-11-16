# delta-doctor

A CLI tool to diagnose and fix Delta Lake table health issues.

## What it does

- Protocol Health: Detects unused writer features (appendOnly, invariants) that break reader compatibility.
- Performance Health: Flags small files that slow down queries.
- Fix: Removes unused protocol features directly from the Delta log.

## Install

    pip install -e .

## Usage

    delta-doctor inspect /path/to/table
    delta-doctor fix /path/to/table --remove-unused

## Why it exists

Delta Lake tables can accumulate unused protocol features that break readers like AWS Athena. This tool catches them before they cause production incidents.

Built by Tabish Sayyed, contributor to delta-rs (PR #5023).
