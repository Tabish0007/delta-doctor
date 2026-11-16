import os
import json
from deltalake import DeltaTable

def analyze(path: str):
    dt = DeltaTable(path)
    p = dt.protocol()
    conf = dt.metadata().configuration or {}
    issues = []
    if p.writer_features:
        if 'appendOnly' in p.writer_features and conf.get('delta.appendOnly') != 'true':
            issues.append('appendOnly')
        if 'invariants' in p.writer_features:
            issues.append('invariants')
    dataset = dt.to_pyarrow_dataset()
    files = dataset.files
    sizes = [os.path.getsize(os.path.join(path, f)) for f in files]
    total = sum(sizes)
    avg = total / len(sizes) if sizes else 0
    small = len([s for s in sizes if s < 32 * 1024 * 1024])
    return dt, p, issues, sizes, avg, small

def remove_unused_features(path: str):
    dt = DeltaTable(path)
    p = dt.protocol()
    conf = dt.metadata().configuration or {}
    to_remove = []
    if p.writer_features:
        if 'appendOnly' in p.writer_features and conf.get('delta.appendOnly') != 'true':
            to_remove.append('appendOnly')
        if 'invariants' in p.writer_features:
            to_remove.append('invariants')
    if not to_remove:
        return []

    log_path = os.path.join(path, "_delta_log")
    latest = sorted(os.listdir(log_path))[-1]
    log_file = os.path.join(log_path, latest)

    with open(log_file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if '"protocol"' in line:
            data = json.loads(line)
            proto = data['protocol']
            new_writer = [w for w in proto.get('writerFeatures', []) if w not in to_remove]
            proto['writerFeatures'] = new_writer if new_writer else None
            lines[i] = json.dumps(data) + '\n'
            break

    with open(log_file, 'w') as f:
        f.writelines(lines)

    return to_remove
