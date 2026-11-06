from pathlib import Path
import pytest
from pydantic import ValidationError
from utils.ai_processor import ClientReport, process_dialog_with_ai
from utils.pdf_generator import generate_pdf

ROOT = Path(__file__).resolve().parents[1]

def test_demo_schema():
    data = ClientReport.model_validate_json((ROOT/'examples'/'demo_report.json').read_text(encoding='utf-8'))
    assert data.client_name
    assert len(data.requirements) > 0

@pytest.mark.parametrize('report_type',['client','spec'])
def test_pdf(report_type, tmp_path):
    data = ClientReport.model_validate_json((ROOT/'examples'/'demo_report.json').read_text(encoding='utf-8'))
    path = generate_pdf(data, report_type, tmp_path)
    assert path.read_bytes().startswith(b'%PDF')

def test_empty_dialog():
    with pytest.raises(ValueError):
        process_dialog_with_ai('  ')

def test_invalid_type(tmp_path):
    data = ClientReport.model_validate_json((ROOT/'examples'/'demo_report.json').read_text(encoding='utf-8'))
    with pytest.raises(ValueError):
        generate_pdf(data, 'unknown', tmp_path)

def test_invalid_json_schema():
    with pytest.raises(ValidationError):
        ClientReport.model_validate({'client_name':'Тест'})
