#!/usr/bin/env python3
"""
Demo script for the integrated explainer video pipeline with TTS
Shows different TTS service options without requiring interactive input
"""

from create_explainer_video import ExplainerVideoCreator


def demo_integrated_pipeline():
    """Demonstrate the integrated pipeline with different TTS options"""
    print("🎬 DEMO: INTEGRATED EXPLAINER VIDEO PIPELINE WITH TTS")
    print("=" * 60)
    
    # Sample text content
    sample_text = """
    Artificial Intelligence is transforming our world in remarkable ways. 
    From healthcare to transportation, AI systems are making decisions that impact millions of lives. 
    Understanding how these systems work is crucial for responsible development and deployment.
    """
    
    print("📝 Sample text:")
    print(sample_text.strip())
    print()
    
    creator = ExplainerVideoCreator()
    
    # Demo 1: Google TTS (default)
    print("🎵 DEMO 1: Google TTS (Default)")
    print("-" * 40)
    
    result1 = creator.create_complete_video_assets(
        sample_text, 
        target_duration=45, 
        segments_count=3,
        enable_tts=True,
        tts_service='gtts',
        tts_kwargs={'lang': 'en'}
    )
    
    if result1:
        print(f"✅ Demo 1 completed: {len(result1['audio_files'])} audio files generated")
    else:
        print("❌ Demo 1 failed")
    
    print()
    
    # Demo 2: Edge TTS (higher quality)
    print("🎵 DEMO 2: Edge TTS (Higher Quality)")
    print("-" * 40)
    
    result2 = creator.create_complete_video_assets(
        sample_text, 
        target_duration=45, 
        segments_count=3,
        enable_tts=True,
        tts_service='edge_tts',
        tts_kwargs={'voice': 'en-US-AriaNeural'}
    )
    
    if result2:
        print(f"✅ Demo 2 completed: {len(result2['audio_files'])} audio files generated")
    else:
        print("❌ Demo 2 failed")
    
    print()
    
    # Demo 3: No TTS (text and images only)
    print("🎵 DEMO 3: No TTS (Text and Images Only)")
    print("-" * 40)
    
    result3 = creator.create_complete_video_assets(
        sample_text, 
        target_duration=45, 
        segments_count=3,
        enable_tts=False
    )
    
    if result3:
        print(f"✅ Demo 3 completed: {len(result3['audio_files'])} audio files (should be 0)")
    else:
        print("❌ Demo 3 failed")
    
    print()
    print("🎉 Demo complete!")
    
    # Summary
    print("📊 SUMMARY:")
    print(f"   Demo 1 (Google TTS): {'✅' if result1 else '❌'}")
    print(f"   Demo 2 (Edge TTS): {'✅' if result2 else '❌'}")
    print(f"   Demo 3 (No TTS): {'✅' if result3 else '❌'}")
    
    if result1 and result2 and result3:
        print("\n🎉 All demos passed! The integrated pipeline is working perfectly.")
        print("💡 You can now use:")
        print("   - python create_explainer_video.py (default with Google TTS)")
        print("   - python create_explainer_video.py --tts-service edge_tts (higher quality)")
        print("   - python create_explainer_video.py --no-tts (text/images only)")
    else:
        print("\n⚠️  Some demos failed. Check the output above for details.")


if __name__ == '__main__':
    demo_integrated_pipeline()
