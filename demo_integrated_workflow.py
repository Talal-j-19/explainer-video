#!/usr/bin/env python3
"""
Demo script for the integrated explainer video workflow
Tests the complete pipeline from text to final video
"""

from create_explainer_video import ExplainerVideoCreator


def demo_integrated_workflow():
    """Demo the complete integrated workflow"""
    print("🎬 DEMO: INTEGRATED EXPLAINER VIDEO WORKFLOW")
    print("=" * 60)
    
    # Sample text content for testing
    sample_text = """
    Artificial Intelligence (AI) is transforming the way we live and work. 
    From virtual assistants to autonomous vehicles, AI technologies are becoming 
    increasingly integrated into our daily lives. Machine learning algorithms 
    can now recognize patterns, make predictions, and learn from data without 
    explicit programming. This revolution is creating new opportunities in 
    healthcare, education, transportation, and many other fields.
    
    The future of AI holds tremendous potential for solving complex problems 
    and improving human capabilities. However, it also raises important 
    questions about ethics, privacy, and the future of work. As we continue 
    to develop these technologies, it's crucial to ensure they benefit 
    humanity while addressing potential risks and challenges.
    """
    
    print("📝 Sample Text Content:")
    print("-" * 40)
    print(sample_text.strip())
    print("-" * 40)
    print()
    
    # Initialize the creator
    print("🚀 Initializing Explainer Video Creator...")
    creator = ExplainerVideoCreator()
    
    # Configure video compiler for demo (720p for faster processing)
    creator.video_compiler.video_width = 1280
    creator.video_compiler.video_height = 720
    creator.video_compiler.fps = 30
    
    print("✅ Creator initialized with 720p video settings")
    print()
    
    # Create complete video assets
    print("🎬 Creating complete explainer video assets...")
    print("This will include:")
    print("  - Text analysis and script generation")
    print("  - Background image generation")
    print("  - TTS audio generation (Edge TTS)")
    print("  - Video compilation")
    print()
    
    try:
        result = creator.create_complete_video_assets(
            text_content=sample_text,
            target_duration=45,  # 45 seconds
            segments_count=5,    # 5 segments
            enable_tts=True,
            tts_service='edge_tts',
            tts_kwargs={'voice': 'en-US-AriaNeural'}
        )
        
        if result:
            print("\n🎉 DEMO SUCCESSFUL!")
            print("=" * 40)
            print(f"📁 Output Directory: {result['output_directory']}")
            print(f"📝 Script File: {result['script_file']}")
            print(f"🎨 Background Images: {len(result['background_images'])}")
            print(f"📝 Text Overlays: {len(result['text_overlays'])}")
            print(f"🗣️  Narration Scripts: {len(result['narration_scripts'])}")
            print(f"🎵 Audio Files: {len(result['audio_files'])}")
            
            if result.get('final_video'):
                print(f"🎬 Final Video: {result['final_video']}")
                print("\n🎊 COMPLETE SUCCESS! Your explainer video is ready!")
                print("💡 Check the generated_videos/ directory for your final video")
            else:
                print("\n⚠️  Video compilation was skipped or failed")
                print("💡 You can manually compile using: python video_compiler.py")
            
            print(f"\n📋 Production Summary: {result['summary_file']}")
            print("📖 Review the summary for complete details and next steps")
            
        else:
            print("\n❌ DEMO FAILED!")
            print("Check the error messages above for details")
            
    except Exception as e:
        print(f"\n💥 DEMO ERROR: {e}")
        print("This might be due to missing dependencies or configuration issues")
        print("Check the troubleshooting section in the README")


if __name__ == '__main__':
    demo_integrated_workflow()
