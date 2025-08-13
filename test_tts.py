#!/usr/bin/env python3
"""
Test script for TTS Processor
Demonstrates cleaning narration text and generating audio
"""

from tts_processor import TTSProcessor


def test_text_cleaning():
    """Test the text cleaning functionality"""
    print("🧪 TESTING TEXT CLEANING")
    print("=" * 40)
    
    processor = TTSProcessor()
    
    # Test cleaning narrations
    cleaned = processor.clean_all_narrations()
    
    if cleaned:
        print(f"\n✅ Successfully cleaned {len(cleaned)} narration files")
        print("\n📋 Sample cleaned text:")
        for narration in cleaned[:3]:  # Show first 3
            print(f"   Segment {narration['segment_number']}:")
            print(f"      Text: {narration['clean_text'][:80]}...")
            print(f"      Title: {narration['metadata'].get('title', 'N/A')}")
            print(f"      Duration: {narration['metadata'].get('duration', 'N/A')}")
            print()
    else:
        print("❌ No narration files found")


def test_audio_generation():
    """Test audio generation with simple fallback"""
    print("🧪 TESTING AUDIO GENERATION")
    print("=" * 40)
    
    processor = TTSProcessor()
    
    # Try to generate audio with simple fallback
    print("🎵 Attempting audio generation with simple fallback...")
    
    try:
        narrations = processor.generate_all_audio('simple')
        if narrations:
            print(f"\n✅ Generated audio for {len(narrations)} segments")
            print("📁 Check the 'video_segments/audio/' directory for results")
        else:
            print("❌ Audio generation failed")
    except Exception as e:
        print(f"❌ Error during audio generation: {e}")


if __name__ == '__main__':
    print("🎬 TTS PROCESSOR TEST SUITE")
    print("=" * 50)
    
    # Test text cleaning
    test_text_cleaning()
    
    print("\n" + "=" * 50)
    
    # Test audio generation
    test_audio_generation()
    
    print("\n🎉 Test suite complete!")
    print("\n💡 Next steps:")
    print("   1. Install TTS packages: pip install gtts edge-tts")
    print("   2. Run: python tts_processor.py --service gtts")
    print("   3. Check 'video_segments/audio/' for generated files")
