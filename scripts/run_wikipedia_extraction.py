#!/usr/bin/env python3
import sys
import os
import argparse
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extractors.wikipedia_extractor import WikipediaExtractor
from src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run Wikipedia Extraction")
    parser.add_argument("url", help="Wikipedia URL to extract")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    
    args = parser.parse_args()
    
    try:
        config = Config()
        extractor = WikipediaExtractor(config)
        logger.info(f"Extracting from: {args.url}")
        
        doc = extractor.extract(args.url)
        output_data = doc.model_dump()
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            logger.info(f"Output saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
            
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
