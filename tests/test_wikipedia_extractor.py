import pytest
from src.extractors.wikipedia_extractor import WikipediaExtractor
from src.models import Document

def test_wikipedia_extractor_init():
    extractor = WikipediaExtractor()
    assert extractor is not None

def test_wikipedia_extractor_extract_success(mocker):
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    
    # Mock requests
    mock_response = mocker.Mock()
    mock_response.text = "<html>Some HTML</html>"
    mock_response.status_code = 200
    mocker.patch("requests.get", return_value=mock_response)
    
    # Mock trafilatura
    # We provide an XML structure similar to what we expect
    xml_content = """
    <doc>
        <head rend="h1">Python (programming language)</head>
        <main>
            <p>Python is a language.</p>
            <head rend="h2">History</head>
            <p>Created in 1991.</p>
            <head rend="h3">Subhistory</head>
            <list>
                <item>Version 1</item>
                <item>Version 2</item>
            </list>
        </main>
    </doc>
    """
    mocker.patch("trafilatura.extract", return_value=xml_content)
    
    extractor = WikipediaExtractor()
    doc = extractor.extract(url)
    
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Python (programming language)"
    assert doc.metadata.source_type == "wiki"
    
    # Check segments
    # 0: "Python is a language." (text)
    # 1: "History" (heading_l2)
    # 2: "Created in 1991." (text)
    # 3: "Subhistory" (heading_l3)
    # 4: list content (text)
    
    assert len(doc.segments) == 5
    assert doc.segments[0].type == "text"
    assert doc.segments[0].content == "Python is a language."
    
    assert doc.segments[1].type == "heading_l2"
    assert doc.segments[1].content == "History"
    
    assert doc.segments[3].type == "heading_l3"
    assert doc.segments[3].content == "Subhistory"
    
    assert doc.segments[4].type == "text"
    assert "- Version 1" in doc.segments[4].content
    assert "- Version 2" in doc.segments[4].content

def test_wikipedia_extractor_extract_empty_content(mocker):
    url = "https://en.wikipedia.org/wiki/Empty"
    
    mock_response = mocker.Mock()
    mock_response.text = "<html></html>"
    mocker.patch("requests.get", return_value=mock_response)
    mocker.patch("trafilatura.extract", return_value=None)
    
    extractor = WikipediaExtractor()
    doc = extractor.extract(url)
    
    assert isinstance(doc, Document)
    assert len(doc.segments) == 0

def test_wikipedia_extractor_requests_error(mocker):
    url = "https://en.wikipedia.org/wiki/Error"
    mocker.patch("requests.get", side_effect=Exception("Network error"))
    
    extractor = WikipediaExtractor()
    with pytest.raises(ValueError, match="Failed to fetch Wikipedia URL"):
        extractor.extract(url)
