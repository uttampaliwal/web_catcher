import pytest
from src.extractors.wiki import WikiExtractor
from src.models import Document

def test_wiki_extractor_init():
    extractor = WikiExtractor()
    assert extractor is not None

def test_wiki_extractor_extract_success(mocker):
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    
    # Mock wikipedia-api
    mock_wiki = mocker.patch("wikipediaapi.Wikipedia")
    mock_page = mocker.Mock()
    mock_page.exists.return_value = True
    mock_page.title = "Python (programming language)"
    mock_page.summary = "Python is a language."
    mock_page.fullurl = url
    
    mock_section = mocker.Mock()
    mock_section.title = "History"
    mock_section.text = "Python was created in 1991."
    mock_section.sections = []
    
    mock_page.sections = [mock_section]
    mock_section.title = "History"
    mock_section.text = "Python was created in 1991."
    mock_section.sections = []
    
    mock_page.sections = [mock_section]
    mock_wiki.return_value.page.return_value = mock_page
    
    extractor = WikiExtractor()
    doc = extractor.extract(url)
    
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Python (programming language)"
    assert len(doc.segments) >= 2 # Summary + History
    assert doc.segments[0].type == "heading_l1"
    assert doc.segments[1].type == "text"
    assert doc.segments[2].type == "heading_l1"
    assert doc.segments[2].content == "History"

def test_wiki_extractor_extract_invalid_url():
    url = "https://example.com"
    extractor = WikiExtractor()
    with pytest.raises(ValueError, match="Invalid Wikipedia URL"):
        extractor.extract(url)

def test_wiki_extractor_page_not_found(mocker):
    url = "https://en.wikipedia.org/wiki/NonExistentPage12345"
    mock_wiki = mocker.patch("wikipediaapi.Wikipedia")
    mock_page = mocker.Mock()
    mock_page.exists.return_value = False
    mock_wiki.return_value.page.return_value = mock_page
    
    extractor = WikiExtractor()
    with pytest.raises(ValueError, match="does not exist"):
        extractor.extract(url)
