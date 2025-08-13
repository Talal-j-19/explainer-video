#!/usr/bin/env python3
"""
Test image generation specifically
"""

from image_generator import ImageGenerator
import json

def test_image_generation():
    """Test the image generation with a simple segment"""
    
    # Create a simple test segment
    test_segment = {
        "segment_number": 1,
        "title": "Test Segment",
        "image_prompt": "Clean modern office with computers and charts",
        "text_overlay": "TEST"
    }
    
    print("🧪 Testing image generation...")
    
    generator = ImageGenerator()
    
    # Test simple background creation
    output_path = generator.output_dir / "test_background.png"
    
    print(f"📁 Output directory: {generator.output_dir}")
    print(f"🖼️  Testing simple background creation...")
    
    success = generator.create_simple_background(test_segment, str(output_path))
    
    if success:
        print(f"✅ Successfully created test image: {output_path}")
        
        # Check if file exists and has content
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"📊 File size: {size} bytes")
        else:
            print("❌ File was not created")
    else:
        print("❌ Failed to create test image")

if __name__ == '__main__':
    test_image_generation()
