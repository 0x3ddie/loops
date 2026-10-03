"""Preview or install the explicit agent-kit inventory. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
HARNESS_FILES = (
    'CORE.md', 'README.md', 'LOOP-DESIGN.md', 'manifest.json', 'scripts/sync.py',
    'validation/test_sync.py', 'validation/test_loop.py', 'validation/test_writing.py',
    'validation/SMOKE-PROMPTS.md', 'validation/RESULTS.md',
    'research/SOURCES.md', 'research/ANTHROPIC-WORKFLOW.md',
    'templates/AGENTS.md.template', 'templates/CLAUDE.md.template', 'templates/HANDOFF.md.template',
)
SOURCE_STATE = '.agents/harness/package-state.json'
APP_STATE = '.agents/harness/state.json'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def within(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise ValueError(f'Invalid relative path: {relative}')
    parts = relative.split('/')
    if any(part in ('', '.', '..') for part in parts):
        raise ValueError(f'Invalid relative path: {relative}')
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()) or target == root.resolve():
        raise ValueError(f'Path escapes its root: {relative}')
    return target


def source_inventory(root: Path) -> dict[str, bytes]:
    root = root.resolve()
    manifest_path = within(root, '.agents/harness/manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported harness manifest version')
    result = {}
    seen = set()

    def include(relative, expected=None):
        if relative.casefold() in seen:
            raise ValueError(f'Duplicate or case-colliding inventory path: {relative}')
        seen.add(relative.casefold())
        data = within(root, relative).read_bytes()
        if expected is not None and digest(data) != expected:
            raise ValueError(f'Reviewed source hash mismatch: {relative}')
        result[relative] = data

    for relative in HARNESS_FILES:
        include('.agents/harness/' + relative)
    for skill in manifest['skills']:
        name = skill['name']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError(f'Invalid skill name: {name}')
        if 'SKILL.md' not in skill['files']:
            raise ValueError(f'Missing SKILL.md: {name}')
        hashes = skill['canonical_current_sha256']
        if set(hashes) != set(skill['files']):
            raise ValueError(f'Incomplete reviewed hashes: {name}')
        for relative in skill['files']:
            # Validate the resource separately so it cannot escape its skill folder.
            within(root / '.agents/skills' / name, relative)
            include(f'.agents/skills/{name}/{relative}', hashes[relative])
    return result


def read_state(home: Path, relative: str, prefix: str) -> dict[str, str]:
    path = within(home, relative)
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('schema_version') != 1 or not isinstance(value.get('files'), dict):
        raise ValueError(f'Invalid installation state: {relative}')
    for key, value_hash in value['files'].items():
        within(home, key)
        if prefix and not key.startswith(prefix):
            raise ValueError(f'Unexpected state entry: {key}')
        if not isinstance(value_hash, str) or not re.fullmatch(r'[0-9a-f]{64}', value_hash):
            raise ValueError(f'Invalid recorded hash: {key}')
    return value['files']


def state_bytes(files: dict[str, bytes]) -> bytes:
    return (json.dumps({'schema_version': 1, 'files': {p: digest(b) for p, b in files.items()}}, indent=2) + '\n').encode('utf-8')


def install(root: Path, home: Path, apply: bool = False) -> dict:
    root, home = root.resolve(), home.resolve()
    if root == home or root.is_relative_to(home / '.agents'):
        raise ValueError('Use a separate repository checkout, not the active .agents directory')
    sources = source_inventory(root)
    sync = runpy.run_path(str(within(root, '.agents/harness/scripts/sync.py')))
    generated = sync['desired_files'](root)
    if set(sources) & set(generated):
        raise ValueError('Source and generated inventory overlap')
    previous_sources = read_state(home, SOURCE_STATE, '.agents/')
    previous_apps = read_state(home, APP_STATE, '')
    if set(previous_sources) & set(previous_apps):
        raise ValueError('Source and generated state overlap')
    previous = {**previous_sources, **previous_apps}
    desired = {**sources, **generated}
    conflicts = []
    for relative in sorted(set(previous) - set(desired)):
        conflicts.append(f'Previously managed file removed from inventory; reconcile manually: {relative}')
    changes = []
    for relative, data in desired.items():
        target = within(home, relative)
        if any(parent.exists() and not parent.is_dir() for parent in target.parents if parent.is_relative_to(home)):
            conflicts.append(f'Destination parent is not a directory: {relative}')
            continue
        if target.exists() and not target.is_file():
            conflicts.append(f'Destination is not a file: {relative}')
            continue
        original = target.read_bytes() if target.exists() else None
        if original == data:
            continue
        changes.append((relative, data, original))
        if original is not None and original.strip() and digest(original) != previous.get(relative):
            conflicts.append(f'Independent or unmanaged file; merge before installing: {relative}')
    for relative, data in ((SOURCE_STATE, state_bytes(sources)), (APP_STATE, state_bytes(generated))):
        target = within(home, relative)
        original = target.read_bytes() if target.exists() else None
        if original != data:
            changes.append((relative, data, original))
    result = {'mode': 'apply' if apply else 'check', 'home': str(home),
              'source_files': len(sources), 'generated_files': len(generated),
              'changes': [item[0] for item in changes], 'conflicts': conflicts,
              'ok': not changes and not conflicts}
    if not apply or conflicts:
        return result
    if changes:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = within(home, '.agents/harness/backups/kit-' + stamp)
        backup.mkdir(parents=True, exist_ok=False)
        receipt = []
        for relative, data, original in changes:
            receipt.append({'path': relative, 'existed': original is not None,
                            'before_sha256': digest(original) if original is not None else None,
                            'after_sha256': digest(data)})
            if original is not None:
                saved = within(backup, relative)
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(original)
        (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        for relative, data, _ in changes:
            target = within(home, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        result['backup'] = str(backup)
    result['ok'] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Apply the previewed source and application changes')
    parser.add_argument('--home', type=Path, default=Path.home(), help='Destination home; defaults to the current user')
    args = parser.parse_args()
    try:
        result = install(ROOT, args.home, args.apply)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
