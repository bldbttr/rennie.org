#!/usr/bin/env python3
"""
Simple utility to read configuration values for bash scripts
"""
import json
import sys
from pathlib import Path

def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to defaults if config file doesn't exist
        return {
            "image_generation": {
                "variations_per_content": 3,
                "cost_per_image": 0.039,
                "model": "gemini-2.5-flash"
            }
        }

def main():
    if len(sys.argv) != 2:
        print("Usage: python read_config.py <key_path>", file=sys.stderr)
        print("Example: python read_config.py image_generation.variations_per_content", file=sys.stderr)
        sys.exit(1)
    
    key_path = sys.argv[1]
    config = load_config()
    
    # Navigate through nested keys
    current = config
    try:
        for key in key_path.split('.'):
            current = current[key]
        print(current)
    except KeyError:
        print(f"Key path '{key_path}' not found in config", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()