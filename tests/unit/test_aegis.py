import asyncio
import pytest
from nexa.core.security import AegisContentFilter

@pytest.mark.asyncio
async def test_aegis_filter_redaction():
    aegis = AegisContentFilter()

    # Test API Key Redaction
    text = "My OpenAI key is sk-abcdefghijklmnopqrstuvwxyz1234567890 and my google key is AIzaSyB-abcdefghijklmnopqrstuvwxyz12345"
    filtered = await aegis.filter_response(text)

    assert "sk-" not in filtered
    assert "AIza" not in filtered
    assert "[REDACTED SECRET]" in filtered

@pytest.mark.asyncio
async def test_aegis_filter_keywords():
    aegis = AegisContentFilter()

    # Test Keyword Protection
    text = "The system uses a FERNET_KEY to protect the ENCRYPTED_SOUL file."
    filtered = await aegis.filter_response(text)

    assert "FERNET_KEY" not in filtered
    assert "ENCRYPTED_SOUL" not in filtered
    assert "[PROTECTED DATA]" in filtered

@pytest.mark.asyncio
async def test_aegis_file_protection():
    aegis = AegisContentFilter()

    assert await aegis.is_file_protected("~/.nexa/soul.enc") == True
    assert await aegis.is_file_protected("/etc/passwd") == False
