#!/usr/bin/env python3
"""
Экспорт данных макета вакансий в статический сайт vacancies_standalone/js/data.js.
Запуск из корня репозитория (danadjango): python3 scripts/export_vacancies_static.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from job_portal_mock import mock_data  # noqa: E402


def main():
    out_dir = ROOT / 'vacancies_standalone' / 'js'
    out_dir.mkdir(parents=True, exist_ok=True)
    cats = {k: {'label': v['label'], 'color': v['color']} for k, v in mock_data.CATEGORY_META.items()}
    jobs = [dict(v) for v in mock_data.MOCK_VACANCIES]
    payload = {'categoryMeta': cats, 'vacancies': jobs}
    (out_dir / 'data.js').write_text(
        '// Автогенерация: python3 scripts/export_vacancies_static.py\n'
        'window.JOB_PORTAL_DATA = '
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + ';\n',
        encoding='utf-8',
    )
    print(f'OK: {len(jobs)} вакансий -> {out_dir / "data.js"}')


if __name__ == '__main__':
    main()
