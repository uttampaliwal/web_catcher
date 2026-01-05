import logging
import requests
from bs4 import BeautifulSoup
from src.extractors.base import BaseExtractor
from src.models import Document, Segment, Metadata

logger = logging.getLogger(__name__)

class StackOverflowExtractor(BaseExtractor):
    def __init__(self, config=None):
        from src.config import Config
        self.config = config or Config()

    def extract(self, url: str) -> Document:
        if "stackoverflow.com" not in url:
            raise ValueError(f"Invalid StackOverflow URL: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Failed to fetch StackOverflow URL: {url} ({e})")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Title
        title_elem = soup.select_one('#question-header h1 a')
        title = title_elem.get_text().strip() if title_elem else "StackOverflow Question"

        metadata = Metadata(
            title=title,
            url=url,
            source_type="stackoverflow",
            additional={"domain": "stackoverflow.com"}
        )

        segments = []

        def parse_post_content(post_div, section_title=None):
            # If section_title is provided, add it as a heading
            if section_title:
                segments.append(Segment(type="heading_l2", content=section_title))
            
            # The body is usually in .s-prose or .js-post-body
            body = post_div.select_one('.js-post-body, .s-prose')
            if not body:
                return

            for element in body.children:
                if element.name == 'p':
                    text = element.get_text().strip()
                    if text:
                        segments.append(Segment(type="text", content=text))
                
                elif element.name == 'pre':
                    # Code block
                    code = element.get_text().strip()
                    if code:
                        segments.append(Segment(type="code", content=code))
                
                elif element.name in ['ul', 'ol']:
                    items = [li.get_text().strip() for li in element.find_all('li')]
                    if items:
                         content = "\n".join(f"- {i}" for i in items)
                         segments.append(Segment(type="text", content=content))
                
                elif element.name in ['h1', 'h2', 'h3']:
                    text = element.get_text().strip()
                    if text:
                        segments.append(Segment(type="heading_l3", content=text))

        # 1. Question
        question_div = soup.select_one('.question')
        if question_div:
            parse_post_content(question_div, "Question")

        # 2. Answers
        answers_divs = soup.select('.answer')
        # Sort or identify accepted?
        # Usually checking class 'accepted-answer' or itemprop="acceptedAnswer"
        
        for answer_div in answers_divs:
            is_accepted = 'accepted-answer' in answer_div.get('class', [])
            
            header = "Accepted Answer" if is_accepted else "Answer"
            
            # Maybe get votes?
            vote_count_elem = answer_div.select_one('.js-vote-count')
            if vote_count_elem:
                header += f" (Votes: {vote_count_elem.get_text().strip()})"
                
            parse_post_content(answer_div, header)

        return Document(metadata=metadata, segments=segments)
