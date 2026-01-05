#!/usr/bin/env python3
import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extractors.stackoverflow import StackOverflowExtractor
from src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_stackoverflow_extraction.py <url> [output_file]")
        sys.exit(1)
        
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "stackoverflow_output.json"
    
    try:
        config = Config()
        extractor = StackOverflowExtractor(config)
        logger.info(f"Extracting from: {url}")
        
        doc = extractor.extract(url)
        output_data = doc.model_dump()
        
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Output saved to {output_file}")
            
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
