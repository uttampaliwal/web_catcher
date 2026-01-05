import trafilatura
from src.extractors.base import BaseExtractor
from src.models import Document, Segment, Metadata
import logging

logger = logging.getLogger(__name__)

class WebExtractor(BaseExtractor):
    def __init__(self, config=None):
        from src.config import Config
        self.config = config or Config()

    def extract(self, url: str) -> Document:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Failed to fetch URL: {url}")
            
        # Get structured XML/JSON or plain text
        # Using XML to manually segment might be better, but trafilatura.extract with output_format="txt" is easiest for now.
        # Let's use metadata extraction too.
        
        metadata_raw = trafilatura.extract_metadata(downloaded)
        content = trafilatura.extract(
            downloaded, 
            include_comments=self.config.get("web.include_comments", False), 
            include_tables=self.config.get("web.include_tables", True), 
            favor_recall=self.config.get("web.favor_recall", True)
        )
        
        metadata = Metadata(
            title=metadata_raw.title if metadata_raw else None,
            author=metadata_raw.author if metadata_raw else None,
            date=metadata_raw.date if metadata_raw else None,
            url=url,
            source_type="web"
        )
        
        segments = []
        if content:
            # Simple segmentation by double newline for now
            # In a more advanced version, we'd parse the HTML/XML for headings
            parts = content.split('\n\n')
            for part in parts:
                if part.strip():
                    segments.append(Segment(type="text", content=part.strip()))
        
        return Document(metadata=metadata, segments=segments)
