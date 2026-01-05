import pytest
from src.extractors.stackoverflow import StackOverflowExtractor
from src.models import Document

def test_stackoverflow_extractor_init():
    extractor = StackOverflowExtractor()
    assert extractor is not None

def test_stackoverflow_extractor_extract_success(mocker):
    url = "https://stackoverflow.com/questions/123/example-header"
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <div id="question-header"><h1><a href="#">Example Header</a></h1></div>
        <div class="question">
            <div class="js-post-body">
                <p>Question body text.</p>
                <pre><code>print('hello')</code></pre>
            </div>
        </div>
        <div class="answer accepted-answer">
             <div class="js-vote-count">10</div>
             <div class="js-post-body">
                <p>Accepted answer text.</p>
            </div>
        </div>
        <div class="answer">
             <div class="js-vote-count">5</div>
             <div class="js-post-body">
                <p>Other answer text.</p>
            </div>
        </div>
    </html>
    """
    mocker.patch("requests.get", return_value=mock_response)
    
    extractor = StackOverflowExtractor()
    doc = extractor.extract(url)
    
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Example Header"
    assert doc.metadata.source_type == "stackoverflow"
    
    segments = doc.segments
    # Expect:
    # 0. Heading (Question)
    # 1. Text (Question body)
    # 2. Code (Question code)
    # 3. Heading (Accepted Answer)
    # 4. Text (Accepted answer)
    # 5. Heading (Answer)
    # 6. Text (Answer)
    
    assert len(segments) == 7
    assert segments[0].type == "heading_l2" and segments[0].content == "Question"
    assert segments[1].type == "text" and segments[1].content == "Question body text."
    assert segments[2].type == "code" and segments[2].content == "print('hello')"
    
    assert segments[3].type == "heading_l2" 
    assert "Accepted Answer" in segments[3].content
    assert "Votes: 10" in segments[3].content
    
    assert segments[5].type == "heading_l2"
    assert "Votes: 5" in segments[5].content

def test_stackoverflow_extractor_invalid_url():
    extractor = StackOverflowExtractor()
    with pytest.raises(ValueError, match="Invalid StackOverflow URL"):
        extractor.extract("https://google.com")
