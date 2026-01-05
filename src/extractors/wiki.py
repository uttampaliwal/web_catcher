import wikipediaapi
from src.extractors.base import BaseExtractor
from src.models import Document, Segment, Metadata
import logging

logger = logging.getLogger(__name__)

class WikiExtractor(BaseExtractor):
    def __init__(self, config=None):
        from src.config import Config
        self.config = config or Config()
        user_agent = self.config.get("wiki.user_agent")
        lang = self.config.get("wiki.language", "en")
        self.wiki = wikipediaapi.Wikipedia(user_agent, lang)

    def extract(self, title_or_url: str) -> Document:
        # Extract title from URL if potential URL
        if 'wikipedia.org' in title_or_url:
            title = title_or_url.split('/')[-1].replace('_', ' ')
        elif title_or_url.startswith('http'):
            raise ValueError(f"Invalid Wikipedia URL: {title_or_url}")
        else:
            title = title_or_url
        
        page = self.wiki.page(title)
        if not page.exists():
            logger.error(f"Wikipedia page '{title}' does not exist.")
            raise ValueError(f"Wikipedia page '{title}' does not exist.")

        metadata = Metadata(
            title=page.title,
            url=page.fullurl,
            source_type="wiki",
            additional={"summary": page.summary[:500] if page.summary else ""}
        )

        segments = []
        
        # Helper to recursively add sections
        def add_sections(sections, level=1):
            for s in sections:
                segments.append(Segment(type=f"heading_l{level}", content=s.title))
                if s.text:
                    for para in s.text.split('\n\n'):
                        if para.strip():
                            segments.append(Segment(type="text", content=para.strip()))
                add_sections(s.sections, level + 1)

        # Add initial summary as a segment
        if page.summary:
            segments.append(Segment(type="heading_l1", content="Summary"))
            for para in page.summary.split('\n\n'):
                if para.strip():
                    segments.append(Segment(type="text", content=para.strip()))

        add_sections(page.sections)

        return Document(metadata=metadata, segments=segments)
