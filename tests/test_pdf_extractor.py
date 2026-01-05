import pytest
from src.extractors.pdf import PDFExtractor
from src.models import Document

def test_pdf_extractor_init():
    extractor = PDFExtractor()
    assert extractor is not None

def test_pdf_extractor_extract_success(mocker):
    path = "dummy.pdf"
    
    # Mock os.path.exists
    mocker.patch("os.path.exists", return_value=True)
    
    # Mock PyMuPDF (fitz)
    mock_fitz = mocker.patch("fitz.open")
    mock_doc = mocker.MagicMock()
    mock_doc.metadata = {"title": "Test PDF", "author": "Test Author"}
    mock_doc.page_count = 1
    
    mock_page = mocker.Mock()
    mock_page.number = 0
    
    # Mock get_text("blocks")
    mock_page.get_text.return_value = [ (0,0,100,100, "Block 1 content", 0, 0), (0,110,100,200, "Block 2 content", 1, 0) ]
    mock_page.find_tables.return_value = []
    mock_page.get_images.return_value = []
    
    mock_doc.__getitem__.return_value = mock_page
    mock_doc.__len__.return_value = 1
    mock_fitz.return_value = mock_doc
    
    extractor = PDFExtractor()
    doc = extractor.extract(path)
    
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Test PDF"
    assert len(doc.segments) == 2
    assert doc.segments[0].content == "Block 1 content"
    assert doc.segments[1].metadata["page"] == "1"
