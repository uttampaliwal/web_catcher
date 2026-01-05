import pytest
import sys
from unittest.mock import patch, MagicMock
from src.main import main
from src.models import Document, Metadata

def test_cli_help(capsys):
    with patch.object(sys, 'argv', ['main.py', '--help']):
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "usage:" in captured.out

def test_cli_extract_web(mocker):
    # Mock WebExtractor
    mock_extractor = mocker.patch("src.main.WebExtractor")
    mock_doc = Document(
        metadata=Metadata(title="Test", source_type="web", url="http://test.com"),
        segments=[]
    )
    mock_extractor.return_value.extract.return_value = mock_doc
    mocker.patch("builtins.open", mocker.mock_open())
    
    with patch.object(sys, 'argv', ['main.py', 'http://test.com', '--output', 'test.json']):
        main()
    
    mock_extractor.return_value.extract.assert_called_once_with("http://test.com")

def test_cli_extract_pdf(mocker):
    # Mock PDFExtractor and os.path.isfile
    mocker.patch("os.path.isfile", return_value=True)
    mock_extractor = mocker.patch("src.main.PDFExtractor")
    mock_doc = Document(
        metadata=Metadata(title="Test PDF", source_type="pdf"),
        segments=[]
    )
    mock_extractor.return_value.extract.return_value = mock_doc
    mocker.patch("builtins.open", mocker.mock_open())
    
    with patch.object(sys, 'argv', ['main.py', 'test.pdf', '--output', 'test.json']):
        main()
    
    mock_extractor.return_value.extract.assert_called_once_with("test.pdf")

def test_cli_auto_detect_wiki(mocker):
    mock_extractor = mocker.patch("src.main.WikiExtractor")
    mock_doc = Document(
        metadata=Metadata(title="Wiki Test", source_type="wiki", url="https://en.wikipedia.org/wiki/Test"),
        segments=[]
    )
    mock_extractor.return_value.extract.return_value = mock_doc
    mocker.patch("builtins.open", mocker.mock_open())
    
    url = "https://en.wikipedia.org/wiki/Test"
    with patch.object(sys, 'argv', ['main.py', url, '--output', 'test.json']):
        main()
    
    mock_extractor.return_value.extract.assert_called_once_with(url)
