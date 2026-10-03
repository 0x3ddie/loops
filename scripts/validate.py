"""Validate reviewed sources and skill metadata. Development dependency: PyYAML."""
import json
from pathlib import Path
import re
import sys

import yaml
from install import ROOT, source_inventory


def validate(root: Path) -> dict:
    files = source_inventory(root)
    errors = []
    names = []
    for relative, data in files.items():
        if not relative.endswith('/SKILL.md'):
            continue
        text = data.decode('utf-8')
        match = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.S)
        if not match:
            errors.append(f'{relative}: missing frontmatter')
            continue
        meta = yaml.safe_load(match[1])
        if not isinstance(meta, dict):
            errors.append(f'{relative}: metadata must be a mapping')
            continue
        name = meta.get('name')
        description = meta.get('description')
        if name != Path(relative).parent.name or not isinstance(description, str) or not description.strip():
            errors.append(f'{relative}: invalid name or description')
        if not isinstance(name, str) or len(name) > 64 or len(description or '') > 1024:
            errors.append(f'{relative}: invalid metadata lengths')
        if isinstance(description, str) and description.lstrip().startswith('[TODO:'):
            errors.append(f'{relative}: unfinished description')
        names.append(name)
        base = root / Path(relative).parent
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in link and not link.startswith('#'):
                resource = (base / link.split('#')[0]).resolve()
                if not resource.is_relative_to(base.resolve()) or not resource.is_file():
                    errors.append(f'{relative}: invalid reference {link}')
        ui = base / 'agents/openai.yaml'
        if ui.exists():
            value = yaml.safe_load(ui.read_text(encoding='utf-8'))
            interface = value.get('interface', {})
            short = interface.get('short_description', '')
            prompt = interface.get('default_prompt', '')
            if not 25 <= len(short) <= 64 or '$' + str(name) not in prompt:
                errors.append(f'{relative}: invalid UI metadata')
    if len(names) != len(set(names)):
        errors.append('Duplicate skill names')
    return {'ok': not errors, 'source_files': len(files), 'skills': len(names), 'errors': errors}


if __name__ == '__main__':
    try:
        result = validate(ROOT)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, indent=2))
        sys.exit(2)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['ok'] else 1)
