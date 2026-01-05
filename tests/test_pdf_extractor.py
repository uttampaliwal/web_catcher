import pytest
from extractors.pdf import PDFExtractor
from models import Document

def test_pdf_extractor_init():
    extractor = PDFExtractor()
    assert extractor is not None

def test_pdf_extractor_extract_success(mocker):
    path = "dummy.pdf"
    
    # Mock PyMuPDF (fitz)
    mock_fitz = mocker.patch("fitz.open")
    mock_doc = mocker.Mock()
    mock_doc.metadata = {"title": "Test PDF"}
    
    mock_page = mocker.Mock()
    mock_page.number = 0
    mock_page.get_text.return_value = "Page 1 Content\nMore text."
    
    # Mock get_text("blocks")
    # Block format: (x0, y0, x1, y1, "text", block_no, block_type)
    mock_page.get_text.side_effect = [
        "Page 1 Content\nMore text.", # Initial text check if any
        [ (0,0,100,100, "Block 1 content", 0, 0), (0,110,100,200, "Block 2 content", 1, 0) ]
    ]
    
    mock_doc.__iter__.return_value = [mock_page]
    mock_doc.__len__.return_value = 1
    mock_fitz.return_value = mock_doc
    
    extractor = PDFExtractor()
    doc = extractor.extract(path)
    
    assert isinstance(doc, Document)
    assert doc.metadata.title == "Test PDF"
    assert len(doc.segments) == 2
    assert doc.segments[0].content == "Block 1 content"
    assert doc.segments[1].metadata["page"] == 1
