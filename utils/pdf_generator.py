import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from weasyprint import HTML

log = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parent.parent

def generate_pdf(data, report_type='client', output_dir=None):
    if report_type not in ('client','spec'):
        raise ValueError('Неизвестный тип отчёта')
    out = Path(output_dir) if output_dir else ROOT / 'reports'
    out.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(ROOT/'templates'), autoescape=select_autoescape(['html']), undefined=StrictUndefined)
    html = env.get_template('report_template.html').render(report=data, report_type=report_type, generated_at=datetime.now().strftime('%d.%m.%Y %H:%M'))
    path = out / f'{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.pdf'
    log.info('Формирование PDF: %s', path)
    HTML(string=html, base_url=str(ROOT)).write_pdf(path)
    log.info('PDF сохранён: %s', path)
    return path
