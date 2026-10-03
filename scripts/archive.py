"""Create a release ZIP from an explicit source inventory, excluding local state."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from install import ROOT, source_inventory, within

EXTRAS = (
    'README.md', 'AGENTS.md', 'THIRD_PARTY_NOTICES.md', 'VALIDATION.md', 'VERSION',
    'requirements-dev.txt', '.gitignore', '.gitattributes', '.github/workflows/validate.yml',
    'scripts/install.py', 'scripts/validate.py', 'scripts/test_install.py', 'scripts/archive.py',
    'validation/job-outreach-cases.md',
)


def archive(output: Path) -> dict:
    files = source_inventory(ROOT)
    files.update({relative: within(ROOT, relative).read_bytes() for relative in EXTRAS})
    output = output.resolve()
    if any(output == within(ROOT, relative) for relative in files):
        raise ValueError('Archive output cannot replace a source file')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for relative, data in sorted(files.items()):
            info = zipfile.ZipInfo('eddie-agent-kit/' + relative)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    with zipfile.ZipFile(output) as bundle:
        if bundle.testzip() is not None:
            raise ValueError('Archive failed its integrity check')
        for relative, expected in files.items():
            if bundle.read('eddie-agent-kit/' + relative) != expected:
                raise ValueError(f'Archive differs from source: {relative}')
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + '.sha256').write_text(f'{checksum}  {output.name}\n', encoding='utf-8')
    return {'archive': str(output), 'files': len(files), 'sha256': checksum, 'verified_against_sources': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / f'eddie-agent-kit-v{version}.zip')
    args = parser.parse_args()
    print(json.dumps(archive(args.output), indent=2))
