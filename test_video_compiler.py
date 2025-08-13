#!/usr/bin/env python3
"""
Test script for video compiler functionality
"""

from video_compiler import VideoCompiler
from pathlib import Path


def test_video_compiler():
    """Test the video compiler functionality"""
    print("🧪 TESTING VIDEO COMPILER")
    print("=" * 50)
    
    # Initialize compiler
    compiler = VideoCompiler()
    
    # Test 1: Check FFmpeg availability
    print("🔍 TEST 1: Checking FFmpeg availability...")
    ffmpeg_available = compiler.check_ffmpeg()
    
    if ffmpeg_available:
        print("✅ FFmpeg is available")
    else:
        print("❌ FFmpeg not found")
        print("   Please install FFmpeg from: https://ffmpeg.org/download.html")
        return False
    
    # Test 2: Check if video script exists
    print("\n🔍 TEST 2: Checking video script...")
    script_file = compiler.video_segments_dir / "video_script.json"
    
    if script_file.exists():
        print("✅ Video script found")
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script = json.load(f)
            segments = script.get('segments', [])
            print(f"   📋 Found {len(segments)} segments")
        except Exception as e:
            print(f"   ❌ Error reading script: {e}")
            return False
    else:
        print("❌ Video script not found")
        print("   Run create_explainer_video.py first to generate video assets")
        return False
    
    # Test 3: Check if audio files exist
    print("\n🔍 TEST 3: Checking audio files...")
    audio_dir = compiler.video_segments_dir / "audio"
    
    if audio_dir.exists():
        audio_files = list(audio_dir.glob("segment_*_audio.mp3"))
        print(f"✅ Found {len(audio_files)} audio files")
        
        for audio_file in audio_files[:3]:  # Show first 3
            print(f"   🎵 {audio_file.name}")
    else:
        print("❌ Audio directory not found")
        print("   Run TTS processor first to generate audio files")
        return False
    
    # Test 4: Check if background images exist
    print("\n🔍 TEST 4: Checking background images...")
    background_images = []
    
    for segment in segments[:3]:  # Check first 3 segments
        bg_image = segment.get('background_image', '')
        if bg_image and Path(bg_image).exists():
            background_images.append(bg_image)
            print(f"   🖼️  {Path(bg_image).name}")
        else:
            print(f"   ❌ Background image missing for segment {segment['segment_number']}")
    
    if background_images:
        print(f"✅ Found {len(background_images)} background images")
    else:
        print("❌ No background images found")
        return False
    
    print("\n🎉 All tests passed! Video compiler is ready to use.")
    print("\n💡 Next steps:")
    print("   1. Run: python video_compiler.py --segments-only")
    print("   2. Run: python video_compiler.py (complete video)")
    print("   3. Check generated_videos/ directory for results")
    
    return True


if __name__ == '__main__':
    import json
    test_video_compiler()
