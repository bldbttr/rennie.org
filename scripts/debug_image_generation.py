#!/usr/bin/env python3
"""
Debug script to understand what the Gemini API returns for image generation.
"""

import os
import google.generativeai as genai
import json

# Set API key
api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE')
genai.configure(api_key=api_key)

# Test the specific model
model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

prompt = "Create a 1024x1024 abstract artwork: Abstract expressionist composition conveying the essence of human desire and fulfillment, flowing organic forms suggesting connection between need and satisfaction, warm resonant colors that evoke joy and utility"

print(f"Testing prompt: {prompt[:100]}...")
print("\nGenerating response...")

try:
    response = model.generate_content(prompt)
    
    print(f"Response type: {type(response)}")
    print(f"Response text: {getattr(response, 'text', 'No text attribute')}")
    
    if hasattr(response, 'parts'):
        print(f"Parts: {len(response.parts) if response.parts else 0}")
        for i, part in enumerate(response.parts or []):
            print(f"  Part {i}: {type(part)}")
            if hasattr(part, 'text'):
                print(f"    Text: {part.text[:100]}...")
            if hasattr(part, 'inline_data'):
                print(f"    Inline data: {part.inline_data is not None}")
                if part.inline_data:
                    print(f"    Mime type: {part.inline_data.mime_type}")
                    print(f"    Data length: {len(part.inline_data.data) if part.inline_data.data else 0}")
    
    # Try to get the full response structure
    print(f"\nFull response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")

print("\nTesting with alternative models...")

# Test with different models
test_models = [
    'gemini-2.0-flash-exp-image-generation',
    'imagen-3.0-generate-002'
]

for model_name in test_models:
    try:
        print(f"\nTesting {model_name}...")
        test_model = genai.GenerativeModel(model_name)
        response = test_model.generate_content("Create an abstract art image")
        print(f"  Success: {type(response)}")
    except Exception as e:
        print(f"  Failed: {e}")

print("\nDebug completed.")