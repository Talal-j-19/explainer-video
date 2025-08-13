#!/usr/bin/env python3
"""
Simple test of the video generator
"""

from video_explainer_generator import VideoExplainerGenerator

def test_simple():
    """Test with very simple text"""
    
    simple_text = "AI helps businesses grow by 25%."
    
    print("🧪 Testing with simple text...")
    print(f"Text: {simple_text}")
    
    try:
        generator = VideoExplainerGenerator()
        
        segments = generator.analyze_text_for_video(
            text_content=simple_text,
            target_duration=15,
            segments_count=2
        )
        
        if segments:
            print(f"✅ Success! Generated {len(segments)} segments")
            for i, seg in enumerate(segments, 1):
                print(f"Segment {i}: {seg.get('title', 'No title')}")
        else:
            print("❌ Failed to generate segments")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple()
