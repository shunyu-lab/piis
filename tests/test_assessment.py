from pathlib import Path

from piis.assessment.bank import QuestionBank, question_bank_from_directory
from piis.assessment.models import AssessmentItem, CognitiveLevel, QuestionType
from piis.assessment.repository import AssessmentItemRepository, JsonAssessmentItemRepository
from piis.config.settings import Settings

ROOT = Path(__file__).resolve().parents[1]
EMPTY_BANK = ROOT / "data" / "assessment" / "questions"
SAMPLE_DATA = ROOT / "examples" / "sample_data"


def test_assessment_item_schema_accepts_in_memory_placeholder() -> None:
    item = AssessmentItem(
        id="schema-test-only",
        topic="schema",
        difficulty="unspecified",
        cognitive_level=CognitiveLevel.RECOGNITION,
        question_type=QuestionType.OTHER,
        prompt="TEST_SCHEMA_ONLY",
        metadata={"purpose": "schema-instantiation"},
    )
    assert item.id == "schema-test-only"
    assert item.cognitive_level is CognitiveLevel.RECOGNITION
    assert item.question_type is QuestionType.OTHER


def test_repository_protocol_is_implemented_by_json_store() -> None:
    repo: AssessmentItemRepository = JsonAssessmentItemRepository(EMPTY_BANK)
    assert repo.get("missing") is None
    assert repo.list_items() == []


def test_empty_question_bank_loads_without_question_files() -> None:
    bank = question_bank_from_directory(EMPTY_BANK)
    assert isinstance(bank, QuestionBank)
    assert bank.list_items() == []
    assert bank.get("anything") is None
    json_files = list(EMPTY_BANK.glob("*.json"))
    assert json_files == []


def test_missing_directory_is_an_empty_bank(tmp_path: Path) -> None:
    bank = question_bank_from_directory(tmp_path / "does-not-exist")
    assert bank.list_items() == []


def test_default_assessment_dir_is_the_empty_bank() -> None:
    assert Settings().assessment_dir == Path("data/assessment/questions")
    bank = question_bank_from_directory(Settings().assessment_dir)
    assert bank.list_items() == []


def test_sample_knowledge_data_has_no_question_bank() -> None:
    assert not (SAMPLE_DATA / "assessment").exists()
    assert list(SAMPLE_DATA.rglob("*question*")) == []


def test_processing_pipeline_does_not_import_assessment() -> None:
    runtime = (ROOT / "src" / "piis" / "runtime.py").read_text(encoding="utf-8")
    processor = (ROOT / "src" / "piis" / "pipeline" / "processor.py").read_text(encoding="utf-8")
    assert "piis.assessment" not in runtime
    assert "piis.assessment" not in processor
