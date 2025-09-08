#!/usr/bin/env python3
"""
Test script to verify Gemini API capabilities and image generation.
"""

import os
import google.generativeai as genai

# Set API key
api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE')
genai.configure(api_key=api_key)

print("Testing Gemini API capabilities...")
print(f"API Key: {api_key[:10]}...")

# List available models
print("\nAvailable models:")
for model in genai.list_models():
    print(f"  {model.name} - {model.description}")
    if hasattr(model, 'supported_generation_methods'):
        print(f"    Methods: {model.supported_generation_methods}")

# Test basic text generation
print("\nTesting text generation...")
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content("Hello, can you generate images?")
print(f"Response: {response.text}")

print("\nAPI test completed.")