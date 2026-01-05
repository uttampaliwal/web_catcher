import fitz  # PyMuPDF
from src.extractors.base import BaseExtractor
from src.models import Document, Segment, Metadata
import os

class PDFExtractor(BaseExtractor):
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
            
            # Simple text extraction for now
            # High-level segmentation: try to identify blocks
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
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                segments.append(Segment(
                        type="image",
                        content=f"Image {img_index} on page {page_num + 1}",
                        metadata={"page": str(page_num + 1), "image_index": str(img_index)}
                    ))

        doc.close()
        return Document(metadata=metadata, segments=segments)
