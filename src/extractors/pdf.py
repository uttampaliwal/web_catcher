import fitz  # PyMuPDF
from src.extractors.base import BaseExtractor
from src.models import Document, Segment, Metadata
import os
import logging

logger = logging.getLogger(__name__)

class PDFExtractor(BaseExtractor):
    def __init__(self, config=None):
        from src.config import Config
        self.config = config or Config()

    def extract(self, file_path: str) -> Document:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        doc = fitz.open(file_path)
        
        doc_metadata = doc.metadata
        metadata = Metadata(
            title=doc_metadata.get('title'),
            author=doc_metadata.get('author'),
            source_type="pdf",
            additional={
                "page_count": str(doc.page_count),
                "format": doc_metadata.get('format', 'PDF')
            }
        )

        segments = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 1. Extract Tables
            # PyMuPDF has table detection features
            if self.config.get("pdf.detect_tables", True):
                tabs = page.find_tables()
                for table_index, tab in enumerate(tabs):
                    segments.append(Segment(
                        type="table",
                        content=str(tab.extract()), # Simple conversion to string list for now
                        metadata={
                            "page": str(page_num + 1),
                            "table_index": str(table_index),
                            "row_count": str(len(tab.extract())),
                            "col_count": str(len(tab.extract()[0]) if tab.extract() else "0")
                        }
                    ))

            # 2. Extract Text Blocks
            blocks = page.get_text("blocks")
            for b in blocks:
                # b = (x0, y0, x1, y1, "text", block_no, block_type)
                text = b[4].strip()
                if text:
                    segments.append(Segment(
                        type="text", 
                        content=text,
                        metadata={"page": str(page_num + 1), "block_no": str(b[5])}
                    ))
            
            # Image extraction (optional, but requested)
            if self.config.get("pdf.extract_images", True):
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    segments.append(Segment(
                            type="image",
                            content=f"Image {img_index} on page {page_num + 1}",
                            metadata={"page": str(page_num + 1), "image_index": str(img_index)}
                        ))

        doc.close()
        return Document(metadata=metadata, segments=segments)
