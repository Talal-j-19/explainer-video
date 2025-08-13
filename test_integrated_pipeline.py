#!/usr/bin/env python3
"""
Test script for integrated explainer video pipeline with TTS
"""

from create_explainer_video import ExplainerVideoCreator


def test_integrated_pipeline():
    """Test the complete pipeline with TTS integration"""
    print("🧪 TESTING INTEGRATED EXPLAINER VIDEO PIPELINE WITH TTS")
    print("=" * 60)
    
    # Sample text content
    sample_text = """
    Freshwater jellyfish are fascinating creatures that live in lakes and rivers. 
    They are small, transparent organisms that drift with the current. 
    These jellyfish have a unique life cycle and can survive in various water conditions.
    """
    
    print("📝 Sample text:")
    print(sample_text.strip())
    print()
    
    # Test 1: Pipeline with TTS enabled
    print("🎬 TEST 1: Complete pipeline with TTS enabled")
    print("-" * 40)
    
    creator = ExplainerVideoCreator()
    result = creator.create_complete_video_assets(
        sample_text, 
        target_duration=30, 
        segments_count=3,
        enable_tts=True,
        tts_service='gtts',
        tts_kwargs={'lang': 'en'}
    )
    
    if result:
        print("✅ Test 1 PASSED: Complete pipeline with TTS")
        print(f"   Generated {len(result['audio_files'])} audio files")
    else:
        print("❌ Test 1 FAILED: Complete pipeline with TTS")
    
    print()
    
    # Test 2: Pipeline without TTS
    print("🎬 TEST 2: Pipeline without TTS")
    print("-" * 40)
    
    result2 = creator.create_complete_video_assets(
        sample_text, 
        target_duration=30, 
        segments_count=3,
        enable_tts=False
    )
    
    if result2:
        print("✅ Test 2 PASSED: Pipeline without TTS")
        print(f"   Audio files: {len(result2['audio_files'])} (should be 0)")
    else:
        print("❌ Test 2 FAILED: Pipeline without TTS")
    
    print()
    print("🎉 Integration test complete!")
    
    if result and result2:
        print("✅ All tests passed! TTS integration is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")


if __name__ == '__main__':
    test_integrated_pipeline()
