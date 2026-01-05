import requests
import trafilatura
from lxml import etree
from bs4 import BeautifulSoup
from src.extractors.base import BaseExtractor
from src.models import Document, Segment, Metadata
import logging

logger = logging.getLogger(__name__)

class GrokipediaExtractor(BaseExtractor):
    def __init__(self, config=None):
        from src.config import Config
        self.config = config or Config()

    def extract(self, url: str) -> Document:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Failed to fetch Grokipedia URL: {url} ({e})")

        html_text = response.text
        # Get XML for structure
        xml_content = trafilatura.extract(html_text, output_format='xml', include_comments=False, favor_recall=True)
        
        if not xml_content:
            content = trafilatura.extract(html_text, favor_recall=True)
            return Document(
                metadata=Metadata(title="Grokipedia Page", url=url, source_type="grokipedia"),
                segments=[Segment(type="text", content=content)] if content else []
            )

        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except Exception as e:
            logger.error(f"XML Parsing Error: {e}")
            return Document(
                metadata=Metadata(title="Grokipedia Page", url=url, source_type="grokipedia"),
                segments=[Segment(type="text", content=trafilatura.extract(html_text))]
            )

        title_node = root.find('.//head[@rend="h1"]')
        title = title_node.text if title_node is not None else "Grokipedia Page"
        
        metadata = Metadata(
            title=title,
            url=url,
            source_type="grokipedia",
            additional={"domain": "grokipedia.com"}
        )

        segments = []
        unwanted_strings = ["Fact-checked by Grok", "Loading edits...", "Edits"]

        def add_segment(type, content):
            if not content: return
            text = content.strip()
            # Strict cleaning for small segments
            if len(text) < 100:
                if any(u == text or u in text for u in unwanted_strings):
                    return
            segments.append(Segment(type=type, content=text))

        main_tag = root.find('main')
        if main_tag is not None:
            if main_tag.text:
                add_segment("text", main_tag.text)

            for element in main_tag:
                if element.tag == 'head':
                    rend = element.get('rend', 'h2')
                    level = rend[1] if len(rend) > 1 and rend[1].isdigit() else "2"
                    head_text = element.xpath('string()').strip()
                    if head_text != title:
                        add_segment(f"heading_l{level}", head_text)
                elif element.tag == 'p':
                    add_segment("text", element.xpath('string()'))
                elif element.tag in ['list', 'ul', 'ol']:
                    items = [li.xpath('string()').strip() for li in element.xpath('.//item')]
                    if items:
                        add_segment("text", "\n".join(f"- {i}" for i in items))
                elif element.tag == 'table':
                    rows = []
                    for row in element.xpath('.//row'):
                        cells = [cell.xpath('string()').strip() for cell in row.xpath('.//cell')]
                        rows.append(" | ".join(cells))
                    if rows:
                        add_segment("text", "\n".join(rows))
                
                if element.tail:
                    add_segment("text", element.tail)

        # REFERENCES FALLBACK
        # If the last segments didn't include actual reference content, fetch it from HTML
        has_refs = any("References" in s.content for s in segments[-5:])
        ref_text_present = any("http" in s.content for s in segments[-5:])
        
        if not ref_text_present:
            soup = BeautifulSoup(html_text, 'html.parser')
            ref_div = soup.find('div', id='references')
            if ref_div:
                # If "References" heading wasn't there, add it
                if not has_refs:
                    segments.append(Segment(type="heading_l2", content="References"))
                
                # Add the references list
                ref_links = ref_div.get_text('\n', strip=True)
                if ref_links:
                    segments.append(Segment(type="text", content=ref_links))

        return Document(metadata=metadata, segments=segments)
