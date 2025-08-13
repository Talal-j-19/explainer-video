#!/usr/bin/env python3
"""
Debug the generated PNG files to see what's wrong
"""

import os
from pathlib import Path

def debug_png_files():
    """Check what's in the generated PNG files"""
    
    video_dir = Path("video_segments")
    png_files = list(video_dir.glob("segment_*_background.png"))
    
    print("🔍 DEBUGGING GENERATED PNG FILES")
    print("=" * 40)
    
    for png_file in png_files:
        print(f"\n📁 File: {png_file.name}")
        
        if png_file.exists():
            file_size = png_file.stat().st_size
            print(f"📊 Size: {file_size} bytes")
            
            # Read the file content
            try:
                with open(png_file, 'rb') as f:
                    content = f.read()
                
                print(f"🔍 Content length: {len(content)} bytes")
                
                if len(content) > 0:
                    # Show first few bytes as hex
                    hex_content = content[:20].hex()
                    print(f"🔢 First 20 bytes (hex): {hex_content}")
                    
                    # Check if it starts with PNG signature
                    png_signature = b'\x89PNG\r\n\x1a\n'
                    if content.startswith(png_signature):
                        print("✅ Valid PNG signature found")
                    else:
                        print("❌ Invalid PNG signature")
                        
                        # Try to decode as text to see what it contains
                        try:
                            text_content = content.decode('utf-8', errors='ignore')
                            print(f"📝 Content as text: {text_content[:100]}...")
                        except:
                            print("❌ Cannot decode as text")
                    
                    # Try to open with PIL to verify it's a valid image
                    try:
                        from PIL import Image
                        img = Image.open(png_file)
                        print(f"✅ Valid image: {img.size} pixels, mode: {img.mode}")
                    except ImportError:
                        print("⚠️  PIL not available for image validation")
                    except Exception as e:
                        print(f"❌ PIL cannot open image: {e}")
                        
                else:
                    print("❌ File is empty")
                    
            except Exception as e:
                print(f"❌ Error reading file: {e}")
        else:
            print("❌ File does not exist")

def test_base64_decoding():
    """Test if the issue is with base64 decoding"""
    
    print("\n🧪 TESTING BASE64 DECODING")
    print("=" * 30)
    
    # Test with a known good base64 encoded image (tiny PNG)
    # This is a 1x1 transparent PNG
    test_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
    
    try:
        import base64
        decoded = base64.b64decode(test_base64)
        
        print(f"✅ Test base64 decoded: {len(decoded)} bytes")
        print(f"🔢 First 20 bytes (hex): {decoded[:20].hex()}")
        
        # Check PNG signature
        png_signature = b'\x89PNG\r\n\x1a\n'
        if decoded.startswith(png_signature):
            print("✅ Test PNG has valid signature")
        else:
            print("❌ Test PNG has invalid signature")
            
        # Save test image
        test_file = Path("video_segments/test_valid.png")
        with open(test_file, 'wb') as f:
            f.write(decoded)
        
        print(f"💾 Saved test image: {test_file}")
        
        # Try to open with PIL
        try:
            from PIL import Image
            img = Image.open(test_file)
            print(f"✅ Test image opens successfully: {img.size}")
        except Exception as e:
            print(f"❌ Test image failed to open: {e}")
            
    except Exception as e:
        print(f"❌ Base64 test failed: {e}")

if __name__ == '__main__':
    debug_png_files()
    test_base64_decoding()
