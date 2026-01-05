import pytest
from extractors.web import WebExtractor
from models import Document, Segment

def test_web_extractor_init():
    extractor = WebExtractor()
    assert extractor is not None

def test_web_extractor_extract_success(mocker, mock_trafilatura, mock_trafilatura_extract):
    url = "https://example.com"
    mock_trafilatura.return_value = "<html>...</html>"
    mock_trafilatura_extract.return_value = "Test Title\n\nThis is a test paragraph.\n\nAnother paragraph."
    
    # Mock metadata extraction
    mocker.patch("trafilatura.extract_metadata", return_value=mocker.Mock(title="Test Title", author="Test Author", date="2024-01-01"))
    
    extractor = WebExtractor()
    doc = extractor.extract(url)
    
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Test Title"
    assert doc.metadata.url == url
    assert len(doc.segments) == 3
    assert doc.segments[1].content == "This is a test paragraph."

def test_web_extractor_extract_fail(mock_trafilatura):
    url = "https://invalid.com"
    mock_trafilatura.return_value = None
    
    extractor = WebExtractor()
    with pytest.raises(ValueError, match=f"Failed to fetch URL: {url}"):
        extractor.extract(url)
