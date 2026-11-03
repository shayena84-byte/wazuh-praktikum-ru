"""Merge reviewed, source-controlled curriculum assets into the original course."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'curriculum'


def expand(modules, lessons, sources):
    original_ids = [lesson['id'] for lesson in lessons]
    by_id = {lesson['id']: lesson for lesson in lessons}
    for name in ('base-1-7', 'base-8-14'):
        asset = json.loads((ASSETS / f'{name}.json').read_text())
        sources.update(asset.get('additional_sources', {}))
        for ident, extra in asset['expansions'].items():
            item = by_id[ident]
            item['theory'] += '\n\n' + extra['theory'].strip()
            item['practice'] += '\n\n### Углублённая лабораторная\n\n' + extra['practice'].strip()
            item['case'] = extra['case']
            item['quiz'].extend(extra['quiz'])
            item['checks'].extend(extra['checks'])
            item['minutes'] += extra.get('minutes_add', 60)
            item['sources'] = list(dict.fromkeys(item['sources'] + extra.get('sources', [])))
    for name in ('ad-network', 'api-production', 'detection-capstone'):
        asset = json.loads((ASSETS / f'{name}.json').read_text())
        sources.update(asset.get('additional_sources', {}))
        modules.extend(asset['modules'])
        lessons.extend(asset['lessons'])
    modules.sort(key=lambda item: item['id'])
    lessons.sort(key=lambda item: (item['module'], item['number']))
    assert [item['id'] for item in lessons[:56]] == original_ids
    for item in lessons:
        item['edition'] = 2
        item['track'] = 'foundation' if item['module'] <= 14 else 'advanced'
    modules[13]['title'] = 'Базовый итоговый проект'
    sources['release4149'] = ['Wazuh 4.14.9: примечания к выпуску', 'https://documentation.wazuh.com/current/release-notes/release-4-14-9.html']

