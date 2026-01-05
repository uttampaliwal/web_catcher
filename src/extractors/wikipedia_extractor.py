import logging
from src.extractors.wiki import WikiExtractor
from src.models import Document, Segment, Metadata

logger = logging.getLogger(__name__)

class WikipediaExtractor(WikiExtractor):
    """A thin wrapper around :class:`WikiExtractor` for clearer naming.

    This class does not add new functionality but allows the rest of the codebase
    to refer to a ``WikipediaExtractor`` which mirrors the behaviour of the existing
    ``WikiExtractor``. Future extensions specific to Wikipedia can be added here.
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.config = config
        from src.config import Config
        self.config = config or Config()

    def extract(self, url: str) -> Document:
        # Import dependencies here to ensure they are available
        import requests
        import trafilatura
        from lxml import etree
        from bs4 import BeautifulSoup
        
        # Handle title/url
        if 'wikipedia.org' not in url and not url.startswith('http'):
             # If it's just a title, construct URL
             clean_title = url.replace(' ', '_')
             url = f"https://en.wikipedia.org/wiki/{clean_title}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Failed to fetch Wikipedia URL: {url} ({e})")

        html_text = response.text
        # Get XML for structure
        xml_content = trafilatura.extract(html_text, output_format='xml', include_comments=False, favor_recall=True)
        
        if not xml_content:
            # Fallback to simple extraction
            content = trafilatura.extract(html_text, favor_recall=True)
            return Document(
                metadata=Metadata(title="Wikipedia Page", url=url, source_type="wiki"),
                segments=[Segment(type="text", content=content)] if content else []
            )

        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except Exception as e:
            logger.error(f"XML Parsing Error: {e}")
            return Document(
                metadata=Metadata(title="Wikipedia Page", url=url, source_type="wiki"),
                segments=[Segment(type="text", content=trafilatura.extract(html_text))]
            )

        title_node = root.find('.//head[@rend="h1"]')
        title = title_node.text if title_node is not None else "Wikipedia Page"
        
        metadata = Metadata(
            title=title,
            url=url,
            source_type="wiki",
            additional={"domain": "wikipedia.org"}
        )

        segments = []
        # Wikipedia often has "Edit", "^", etc. Trafilatura cleans a lot but we might want more.
        # Citations often appear as [1] which is good.
        
        def add_segment(type, content):
            if not content: return
            text = content.strip()
            if not text: return
            segments.append(Segment(type=type, content=text))

        main_tag = root.find('main')
        if main_tag is not None:
            # Main intro text often in main_tag.text or first paragraphs
            if main_tag.text:
                add_segment("text", main_tag.text)

            for element in main_tag:
                if element.tag == 'head':
                    rend = element.get('rend', 'h2')
                    # Trafilatura levels: h1 is title. h2 are sections.
                    level = rend[1] if len(rend) > 1 and rend[1].isdigit() else "2"
                    head_text = element.xpath('string()').strip()
                    if head_text != title and head_text not in ["Contents", "Navigation menu"]:
                        add_segment(f"heading_l{level}", head_text)
                elif element.tag == 'p':
                    add_segment("text", element.xpath('string()'))
                elif element.tag in ['list', 'ul', 'ol']:
                    items = [li.xpath('string()').strip() for li in element.xpath('.//item')]
                    if items:
                         # Output list as textual bullet points
                        add_segment("text", "\n".join(f"- {i}" for i in items))
                elif element.tag == 'table':
                    rows = []
                    for row in element.xpath('.//row'):
                        cells = [cell.xpath('string()').strip() for cell in row.xpath('.//cell')]
                        rows.append(" | ".join(cells))
                    if rows:
                        add_segment("text", "\n".join(rows))
                
                # Check for tail text
                if element.tail:
                    add_segment("text", element.tail)

        # Handle References if not captured
        # Trafilatura often captures them if they are in the main text flow.
        # But specifically extracting the References section if missed:
        # We can rely on the headings captured. 
        # "References" heading usually exists in Wikipedia.
        
        return Document(metadata=metadata, segments=segments)
