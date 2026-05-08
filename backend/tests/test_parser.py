import pytest
from app.services.parser_service import extract_profile_from_text, _extract_with_fallback
from app.schemas import ResumeProfile

def test_fallback_parser_email_phone():
    text = "John Doe, email: john@example.com, phone: +1-555-0199"
    profile = _extract_with_fallback(text)
    assert profile.email == "john@example.com"
    assert "+1-555-0199" in profile.phone

def test_fallback_parser_skills():
    text = "I am a Python developer who knows Javascript and SQL. I have great Leadership skills."
    profile = _extract_with_fallback(text)
    skill_names = [s.name for s in profile.skills]
    assert "Python" in skill_names
    assert "Javascript" in skill_names
    assert "SQL" in skill_names
    assert "Leadership" in skill_names

def test_extract_profile_empty_text():
    profile, method = extract_profile_from_text("")
    assert isinstance(profile, ResumeProfile)
    assert method == "fallback"

def test_fallback_suggested_roles():
    text = "I love Python and FastAPI"
    profile = _extract_with_fallback(text)
    assert "Python Developer" in profile.suggested_roles
