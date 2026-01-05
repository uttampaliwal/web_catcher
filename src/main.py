import sys
import argparse
import json
from src.extractors.web import WebExtractor
from src.extractors.wikipedia_extractor import WikipediaExtractor
from src.extractors.pdf import PDFExtractor
from src.extractors.grokipedia import GrokipediaExtractor
from src.config import Config

def main():
    parser = argparse.ArgumentParser(description="Web Catcher: Multi-Data Extraction Tool")
    parser.add_argument("source", help="URL or path to PDF file")
    parser.add_argument("--type", choices=["web", "wiki", "pdf", "auto"], default="auto", help="Source type")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument("--config", help="Path to config yaml file")
    
    args = parser.parse_args()
    config = Config(args.config)
    
    # Simple auto-detection
    source_type = args.type
    if source_type == "auto":
        if args.source.endswith(".pdf"):
            source_type = "pdf"
        elif "wikipedia.org" in args.source:
            source_type = "wiki"
        elif "grokipedia.com" in args.source:
            source_type = "grokipedia"
        else:
            source_type = "web"

    try:
        if source_type == "web":
            extractor = WebExtractor(config)
        elif source_type == "wiki":
            extractor = WikipediaExtractor(config)
        elif source_type == "grokipedia":
            extractor = GrokipediaExtractor(config)
        else:
            extractor = PDFExtractor(config)

        doc = extractor.extract(args.source)
        
        output_data = doc.model_dump()
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Extraction successful. Output saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
