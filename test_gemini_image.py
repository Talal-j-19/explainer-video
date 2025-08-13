#!/usr/bin/env python3
"""
Test Gemini image generation specifically
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_image_generation():
    """Test Gemini 2.0 Flash image generation"""
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY2")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY2 not found")
        return False
    
    genai.configure(api_key=api_key)
    
    print("🧪 Testing Gemini 2.0 Flash image generation...")
    
    try:
        # Use the image generation model
        model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
        
        prompt = "A clean, modern office with computers and charts, professional style, 16:9 aspect ratio"
        
        print(f"📝 Prompt: {prompt}")
        print("🔄 Generating image...")
        
        # Try different approaches
        
        # Approach 1: With proper response modalities
        try:
            # Configure generation to request both image and text
            generation_config = {
                "response_modalities": ["IMAGE", "TEXT"]
            }

            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            print("✅ Response received")
            
            if hasattr(response, 'candidates') and response.candidates:
                print(f"📊 Found {len(response.candidates)} candidates")
                
                for i, candidate in enumerate(response.candidates):
                    print(f"Candidate {i+1}:")
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        print(f"  Parts: {len(candidate.content.parts)}")
                        
                        for j, part in enumerate(candidate.content.parts):
                            print(f"  Part {j+1}: {type(part)}")
                            if hasattr(part, 'text'):
                                print(f"    Text: {part.text[:100]}...")
                            if hasattr(part, 'inline_data'):
                                print(f"    Inline data: {part.inline_data.mime_type if part.inline_data else 'None'}")

                                if part.inline_data:
                                    # Get the image data
                                    image_data = part.inline_data.data

                                    print(f"    Raw data type: {type(image_data)}")
                                    print(f"    Raw data length: {len(image_data)}")

                                    # Check if it's already binary data or base64 string
                                    if isinstance(image_data, bytes):
                                        print("    ✅ Data is already binary")
                                        image_bytes = image_data
                                    else:
                                        print("    🔄 Data is string, decoding base64...")
                                        import base64
                                        # Clean and decode base64
                                        clean_data = image_data.replace('\n', '').replace('\r', '').replace(' ', '')
                                        image_bytes = base64.b64decode(clean_data)

                                    print(f"    Final bytes: {len(image_bytes)}")
                                    print(f"    First 20 bytes (hex): {image_bytes[:20].hex()}")

                                    # Check PNG signature
                                    png_signature = b'\x89PNG\r\n\x1a\n'
                                    if image_bytes.startswith(png_signature):
                                        print("    ✅ Valid PNG signature")
                                    else:
                                        print("    ❌ Invalid PNG signature")

                                    output_path = Path("video_segments") / "test_gemini_image.png"
                                    output_path.parent.mkdir(exist_ok=True)

                                    with open(output_path, 'wb') as f:
                                        f.write(image_bytes)

                                    file_size = output_path.stat().st_size
                                    print(f"✅ Image saved: {output_path} ({file_size} bytes)")

                                    # Try to verify with PIL
                                    try:
                                        from PIL import Image
                                        img = Image.open(output_path)
                                        print(f"✅ PIL verification: {img.size} pixels")
                                    except Exception as e:
                                        print(f"❌ PIL verification failed: {e}")

                                    return True
            else:
                print("❌ No candidates in response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Check if it's the modality error
            if "response modalities" in str(e):
                print("ℹ️  This is the expected modality error")
                print("💡 The model requires specific configuration for image generation")
            
        return False
        
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

if __name__ == '__main__':
    success = test_gemini_image_generation()
    if success:
        print("🎉 Gemini image generation test passed!")
    else:
        print("💥 Gemini image generation test failed!")
