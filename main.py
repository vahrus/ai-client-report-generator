import argparse
import json
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from utils.ai_processor import ClientReport, process_dialog_with_ai
from utils.pdf_generator import generate_pdf

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description='Генератор PDF-отчётов из клиентских диалогов')
    parser.add_argument('dialog', nargs='?', help='Путь к UTF-8 файлу диалога')
    parser.add_argument('--type', choices=['client','spec'], default='client', help='Тип PDF')
    parser.add_argument('--demo', action='store_true', help='Демо-данные без API (не AI-обработка)')
    args = parser.parse_args()
    load_dotenv(ROOT/'.env')
    (ROOT/'logs').mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.StreamHandler(), logging.FileHandler(ROOT/'logs'/'app.log', encoding='utf-8')])
    log = logging.getLogger(__name__)
    try:
        if args.demo:
            log.info('Демонстрационный режим: JSON из примера, без вызова ИИ')
            data = ClientReport.model_validate_json((ROOT/'examples'/'demo_report.json').read_text(encoding='utf-8'))
        else:
            if not args.dialog:
                parser.error('Укажите путь к диалогу или --demo')
            text = Path(args.dialog).read_text(encoding='utf-8')
            log.info('Прочитан диалог: %s (%s символов)', args.dialog, len(text))
            data = process_dialog_with_ai(text)
        path_json = ROOT/'reports'/f'{args.type}_latest.json'
        path_json.parent.mkdir(exist_ok=True)
        path_json.write_text(data.model_dump_json(indent=2), encoding='utf-8')
        log.info('Структурированный JSON сохранён: %s', path_json)
        pdf = generate_pdf(data, args.type)
        print(f'Отчёт успешно создан: {pdf}')
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        log.exception('Ошибка обработки: %s', exc)
        return 1
    except Exception:
        log.exception('Неожиданная ошибка')
        return 1

if __name__ == '__main__':
    sys.exit(main())
