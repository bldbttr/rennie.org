#!/usr/bin/env python3
"""
Test script for Nano Banana (Gemini 2.5 Flash Image)
Generates an image and saves it locally
"""

import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

def test_nano_banana():
    """Test nano banana with a simple prompt"""
    # Your API key (replace with your actual key)
    api_key = "AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE"
    
    client = genai.Client(api_key=api_key)
    
    # Test prompt for Paul Graham quote visualization
    prompt = """Make something people want"""
    
    try:
        print("🍌 Generating image with Nano Banana...")
        print(f"Prompt: {prompt}")
        print()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
        )
        
        print("📊 Response metadata:")
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            print(f"  Total tokens: {usage.total_token_count}")
            print(f"  Image tokens: {usage.candidates_token_count}")
            print(f"  Estimated cost: ${(usage.candidates_token_count / 1000000) * 30:.4f}")
        
        # Process the response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Decode the base64 image data
                image_data = part.inline_data.data
                image = Image.open(BytesIO(image_data))
                
                # Save the image
                filename = "paul_graham_quote.png"
                image.save(filename)
                
                print(f"✅ Image saved as: {filename}")
                print(f"   Size: {image.size}")
                print(f"   Format: {image.format}")
                print(f"   Mode: {image.mode}")
                
                return True
                
            elif part.text is not None:
                print(f"📝 Text response: {part.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_idea_lightbulb():
    """Test with the lightbulb prompt from your curl test"""
    api_key = "AIzaSyCh41VaooU6xexjq7zndc7FSNOh2Sg4-EE"
    client = genai.Client(api_key=api_key)
    
    prompt = "Create a minimalist illustration of a lightbulb with the word IDEA inside it"
    
    try:
        print("🍌 Testing lightbulb illustration...")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
        )
        
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save("lightbulb_idea.png")
                print("✅ Lightbulb image saved as: lightbulb_idea.png")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Nano Banana Image Generation")
    print("=" * 50)
    
    # Test 1: Lightbulb (matching your curl test)
    print("\n1️⃣ Testing lightbulb illustration...")
    test_idea_lightbulb()
    
    # Test 2: Paul Graham quote visualization
    print("\n2️⃣ Testing Paul Graham quote visualization...")
    test_nano_banana()
    
    print("\n🎉 Tests complete! Check the generated PNG files.")
