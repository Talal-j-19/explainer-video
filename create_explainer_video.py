#!/usr/bin/env python3
"""
Complete Explainer Video Creator
Combines text analysis, image generation, and asset preparation for video creation
"""

import os
import sys
from pathlib import Path
from video_explainer_generator import VideoExplainerGenerator
from image_generator import ImageGenerator
from tts_processor import TTSProcessor
from video_compiler import VideoCompiler
import time


class ExplainerVideoCreator:
    def create_text_overlay_coordinate_files(self, script):
        """
        For each segment, generate a file with overlay text and coordinates for the corresponding image using Gemini.
        Returns a list of generated JSON file paths.
        """
        from image_generator import gemini_image_prompt
        import json
        import re
        overlay_coord_files = []
        for segment in script['segments']:
            segment_num = segment['segment_number']
            overlay_text = segment.get('text_overlay', '')
            image_path = segment.get('background_image', '')
            coords = None
            if overlay_text and image_path and os.path.exists(image_path):
                # Call Gemini API for coordinates (multi-part)
                coords_text = gemini_image_prompt(image_path, overlay_text)
                coords = None
                if coords_text:
                    try:
                        # Extract JSON array from response
                        match = re.search(r'\[.*\]', coords_text, re.DOTALL)
                        if match:
                            coords = json.loads(match.group(0))
                    except Exception:
                        pass
                if not coords or not isinstance(coords, list):
                    print(f"⚠️  Falling back to default coordinates for segment {segment_num}")
                    # Fallback: treat the whole overlay as one part
                    coords = [{
                        "text": overlay_text,
                        "x": 100, "y": 100, "width": 600, "height": 120
                    }]
                overlay_coord = {
                    "segment_number": segment_num,
                    "title": segment.get('title', ''),
                    "overlay_text": overlay_text,
                    "coordinates": coords,
                    "background_image": image_path
                }
                coord_file = self.output_dir / f"segment_{segment_num:02d}_overlay_coords.json"
                with open(coord_file, 'w', encoding='utf-8') as f:
                    json.dump(overlay_coord, f, indent=2, ensure_ascii=False)
                overlay_coord_files.append(str(coord_file))
                print(f"✅ Created overlay coordinate file: {coord_file}")
        return overlay_coord_files
    """Complete pipeline for creating explainer video assets"""
    
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else Path("video_segments")
        self.video_generator = VideoExplainerGenerator(self.output_dir)
        self.image_generator = ImageGenerator(self.output_dir)
        self.tts_processor = TTSProcessor(self.output_dir)
        self.video_compiler = VideoCompiler(self.output_dir)
        
    def create_complete_video_assets(self, text_content, target_duration=60, segments_count=None, 
                                   enable_tts=True, tts_service='gtts', tts_kwargs=None):
        """
        Create all assets needed for explainer video
        
        Args:
            text_content: Input text to convert to video
            target_duration: Target video duration in seconds
            segments_count: Number of segments (auto-calculated if None)
            enable_tts: Whether to generate audio using TTS
            tts_service: TTS service to use ('gtts', 'edge_tts', 'azure', 'simple')
            tts_kwargs: Additional arguments for TTS service
        
        Returns:
            Dictionary with paths to all generated assets
        """
        if tts_kwargs is None:
            tts_kwargs = {}
        print("🚀 CREATING COMPLETE EXPLAINER VIDEO ASSETS")
        print("=" * 60)
        
        # Step 1: Generate video script and segments
        print("\n📝 STEP 1: Generating video script...")
        result = self.video_generator.generate_explainer_video_plan(
            text_content, target_duration, segments_count
        )
        
        if not result:
            print("❌ Failed to generate video script")
            return None
        
        script_path = result['script_path']
        script = result['script']
        
        # Step 2: Generate background images
        print("\n🎨 STEP 2: Generating background images...")
        images_success = self.image_generator.generate_images_for_script(script_path)
        
        # Step 3: Create text overlay files
        print("\n📝 STEP 3: Creating text overlay files...")
        overlay_files = self.create_text_overlay_files(script)

        # Step 4: Create narration scripts
        print("\n🗣️  STEP 4: Creating narration scripts...")
        narration_files = self.create_narration_files(script)
        
        # Step 5: Generate audio from narration scripts (if enabled)
        if enable_tts:
            print(f"\n🎵 STEP 5: Generating audio from narration scripts using {tts_service}...")
            audio_files = self.generate_audio_from_narrations(tts_service, tts_kwargs)
        else:
            print("\n🎵 STEP 5: Skipping TTS audio generation...")
            audio_files = []
        
        # Step 6: Compile complete video (if enabled)
        if enable_tts and audio_files and not getattr(self, 'skip_video_compilation', False):
            print("\n🎬 STEP 6: Compiling complete video...")
            final_video = self.compile_complete_video()
            if final_video:
                print(f"✅ Video compilation successful: {final_video}")
            else:
                print("⚠️  Video compilation failed, continuing with assets...")
                final_video = None
        else:
            print("\n🎬 STEP 6: Skipping video compilation (no audio, TTS disabled, or video compilation disabled)...")
            final_video = None
        
        # Step 7: Generate summary and next steps
        print("\n📋 STEP 7: Creating production summary...")
        summary_file = self.create_production_summary(script, overlay_files, narration_files, audio_files, final_video)
        
        assets = {
            "script_file": script_path,
            "background_images": [seg['background_image'] for seg in script['segments']],
            "text_overlays": overlay_files,
            # "overlay_coord_files": overlay_coord_files,
            "narration_scripts": narration_files,
            "audio_files": audio_files,
            "final_video": final_video,
            "summary_file": summary_file,
            "output_directory": str(self.output_dir)
        }
        
        self.print_final_summary(assets, script)
        
        return assets
    
    def create_text_overlay_files(self, script):
        """Create individual text files for each segment's overlay text"""
        overlay_files = []
        
        for segment in script['segments']:
            segment_num = segment['segment_number']
            overlay_text = segment.get('text_overlay', '')
            
            if overlay_text:
                overlay_file = self.output_dir / f"segment_{segment_num:02d}_overlay.txt"
                
                with open(overlay_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Text Overlay for Segment {segment_num}\n")
                    f.write(f"# Title: {segment['title']}\n\n")
                    f.write(overlay_text)
                
                overlay_files.append(str(overlay_file))
                print(f"✅ Created overlay text: {overlay_file}")
        
        return overlay_files
    
    def create_narration_files(self, script):
        """Create narration script files for TTS"""
        narration_files = []
        
        # Individual segment narrations
        for segment in script['segments']:
            segment_num = segment['segment_number']
            narration_text = segment.get('narration_text', '')
            
            narration_file = self.output_dir / f"segment_{segment_num:02d}_narration.txt"
            
            with open(narration_file, 'w', encoding='utf-8') as f:
                f.write(f"# Narration for Segment {segment_num}\n")
                f.write(f"# Title: {segment['title']}\n")
                f.write(f"# Duration: {segment.get('duration_seconds', 10)} seconds\n\n")
                f.write(narration_text)
            
            narration_files.append(str(narration_file))
            print(f"✅ Created narration script: {narration_file}")
        
        # Complete narration script
        complete_narration = self.output_dir / "complete_narration.txt"
        
        with open(complete_narration, 'w', encoding='utf-8') as f:
            f.write("# Complete Video Narration Script\n")
            f.write(f"# Total Duration: {script['video_metadata']['estimated_duration']} seconds\n\n")
            
            for segment in script['segments']:
                f.write(f"## Segment {segment['segment_number']}: {segment['title']}\n")
                f.write(f"Duration: {segment.get('duration_seconds', 10)} seconds\n")
                f.write(f"Timing: {segment['timing']['start_time']}s - {segment['timing']['end_time']}s\n\n")
                f.write(f"{segment.get('narration_text', '')}\n\n")
                f.write("-" * 50 + "\n\n")
        
        narration_files.append(str(complete_narration))
        print(f"✅ Created complete narration: {complete_narration}")
        
        return narration_files
    
    def generate_audio_from_narrations(self, tts_service='gtts', tts_kwargs=None):
        """Generate audio files from narration scripts using TTS"""
        if tts_kwargs is None:
            tts_kwargs = {}
            
        try:
            print(f"🎵 Starting TTS audio generation with {tts_service}...")
            
            # Use the TTS processor to generate audio for all narrations
            narrations = self.tts_processor.generate_all_audio(tts_service, **tts_kwargs)
            
            if narrations:
                # Extract audio file paths from successful generations
                audio_files = []
                for narration in narrations:
                    if narration.get('audio_generated'):
                        audio_file = narration.get('audio_file', '')
                        if audio_file:
                            audio_files.append(audio_file)
                
                # Check for complete audio file
                complete_audio = self.output_dir / "audio" / "complete_narration_audio.mp3"
                if complete_audio.exists():
                    audio_files.append(str(complete_audio))
                
                print(f"✅ Generated {len(audio_files)} audio files")
                return audio_files
            else:
                print("⚠️  No audio files generated")
                return []
                
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
            print("⚠️  Continuing without audio generation...")
            return []
    
    def compile_complete_video(self):
        """Compile complete explainer video from all segments"""
        try:
            print("🎬 Starting video compilation...")
            
            # Set video compiler to use our output directory
            # Must be a Path, not str, because compiler uses Path division with '/'
            self.video_compiler.video_segments_dir = self.output_dir
            self.video_compiler.output_dir = Path("generated_videos")
            
            # Compile complete video
            final_video = self.video_compiler.compile_complete_video()
            
            if final_video:
                print(f"🎉 Video compilation successful!")
                return final_video
            else:
                print("❌ Video compilation failed")
                return None
                
        except Exception as e:
            print(f"❌ Error during video compilation: {e}")
            return None
    
    def create_production_summary(self, script, overlay_files, narration_files, audio_files, final_video=None):
        """Create a production summary with all details and next steps"""
        summary_file = self.output_dir / "production_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Explainer Video Production Summary\n\n")
            
            # Video metadata
            metadata = script['video_metadata']
            f.write("## Video Details\n")
            f.write(f"- **Total Segments**: {metadata['total_segments']}\n")
            f.write(f"- **Estimated Duration**: {metadata['estimated_duration']} seconds\n")
            f.write(f"- **Created**: {metadata['created_at']}\n")
            f.write(f"- **Format**: {metadata['format']}\n\n")
            
            # Segments overview
            f.write("## Segments Overview\n\n")
            for segment in script['segments']:
                f.write(f"### Segment {segment['segment_number']}: {segment['title']}\n")
                f.write(f"- **Duration**: {segment.get('duration_seconds', 10)} seconds\n")
                f.write(f"- **Timing**: {segment['timing']['start_time']}s - {segment['timing']['end_time']}s\n")
                f.write(f"- **Background Image**: `{Path(segment['background_image']).name}`\n")
                f.write(f"- **Text Overlay**: {segment.get('text_overlay', 'None')}\n")
                f.write(f"- **Narration**: {segment.get('narration_text', '')[:100]}...\n\n")
            
            # File assets
            f.write("## Generated Assets\n\n")
            f.write("### Background Images\n")
            for segment in script['segments']:
                f.write(f"- `{Path(segment['background_image']).name}` - Segment {segment['segment_number']}\n")
            
            f.write("\n### Text Overlay Files\n")
            for overlay_file in overlay_files:
                f.write(f"- `{Path(overlay_file).name}`\n")
            
            f.write("\n### Narration Scripts\n")
            for narration_file in narration_files:
                f.write(f"- `{Path(narration_file).name}`\n")
            
            f.write("\n### Audio Files\n")
            if audio_files:
                for audio_file in audio_files:
                    f.write(f"- `{Path(audio_file).name}`\n")
                f.write("\n✅ **Audio generation complete!** All narration has been converted to MP3 files.\n")
            else:
                f.write("- No audio files generated\n")
                f.write("\n⚠️  **Audio generation needed** - Use TTS to convert narration scripts to audio.\n")
            
            # Video compilation status
            f.write("\n### Final Video\n")
            if final_video:
                f.write(f"- `{Path(final_video).name}`\n")
                f.write("\n🎉 **Video compilation complete!** Your explainer video is ready for sharing.\n")
            else:
                f.write("- No final video generated\n")
                f.write("\n⚠️  **Video compilation needed** - Use the integrated video compiler.\n")
            
            # Next steps
            f.write("\n## Next Steps for Video Production\n\n")
            if final_video:
                f.write("### 1. Review Final Video ✅\n")
                f.write("- Watch the complete explainer video\n")
                f.write("- Check audio synchronization with visuals\n")
                f.write("- Verify video quality meets your standards\n\n")
                
                f.write("### 2. Share Your Video ✅\n")
                f.write("- Upload to social media platforms\n")
                f.write("- Embed in websites or presentations\n")
                f.write("- Use in marketing campaigns\n")
                f.write("- Further edit in video software if needed\n\n")
            elif audio_files:
                f.write("### 1. Review Generated Audio ✅\n")
                f.write("- Listen to generated audio files for quality\n")
                f.write("- Audio files are ready for video production\n\n")
                
                f.write("### 2. Compile Video\n")
                f.write("```bash\n")
                f.write("# Use the integrated video compiler\n")
                f.write("python video_compiler.py --resolution 720p\n")
                f.write("```\n\n")
            else:
                f.write("### 1. Generate Audio (TTS)\n")
                f.write("```bash\n")
                f.write("# Use your preferred TTS service to convert narration files to audio\n")
                f.write("# Example with gTTS (Google Text-to-Speech):\n")
                f.write("pip install gtts\n")
                for segment in script['segments']:
                    f.write(f"gtts-cli -f segment_{segment['segment_number']:02d}_narration.txt -o segment_{segment['segment_number']:02d}_audio.mp3\n")
                f.write("```\n\n")
            
            f.write("### 3. Alternative: Use Video Editing Software\n")
            f.write("- Import background images into your video editor\n")
            f.write("- Add text overlays using the provided text files\n")
            f.write("- Import generated audio files\n")
            f.write("- Sync audio with visuals according to timing information\n\n")
            
            f.write("### 4. Recommended Tools\n")
            f.write("- **TTS**: Google Cloud TTS, Amazon Polly, Azure Speech, or gTTS\n")
            f.write("- **Video Editing**: FFmpeg (command line), DaVinci Resolve (free), Adobe Premiere\n")
            f.write("- **Text Overlays**: Can be added in video editor or with FFmpeg\n")
        
        print(f"✅ Created production summary: {summary_file}")
        return str(summary_file)
    
    def print_final_summary(self, assets, script):
        """Print final summary of generated assets"""
        print("\n" + "=" * 60)
        print("🎉 EXPLAINER VIDEO ASSETS GENERATED SUCCESSFULLY!")
        print("=" * 60)
        
        print(f"\n📁 **Output Directory**: {assets['output_directory']}")
        print(f"📋 **Video Script**: {Path(assets['script_file']).name}")
        print(f"🎨 **Background Images**: {len(assets['background_images'])} files")
        print(f"📝 **Text Overlays**: {len(assets['text_overlays'])} files")
        print(f"🗣️  **Narration Scripts**: {len(assets['narration_scripts'])} files")
        print(f"🎵 **Audio Files**: {len(assets['audio_files'])} files")
        if assets.get('final_video'):
            print(f"🎬 **Final Video**: {Path(assets['final_video']).name}")
        print(f"📊 **Production Summary**: {Path(assets['summary_file']).name}")
        
        total_duration = script['video_metadata']['estimated_duration']
        print(f"\n⏱️  **Estimated Video Duration**: {total_duration} seconds ({total_duration//60}:{total_duration%60:02d})")
        
        print(f"\n📋 **Next Steps**:")
        print(f"1. Review the production summary: {Path(assets['summary_file']).name}")
        if assets.get('final_video'):
            print(f"2. 🎉 Video compilation complete - ready for sharing!")
            print(f"3. Your explainer video is ready to use!")
        elif assets['audio_files']:
            print(f"2. ✅ Audio generation complete - ready for video production!")
            print(f"3. Use integrated video compiler: python video_compiler.py")
        else:
            print(f"2. Generate audio from narration scripts using TTS")
            print(f"3. Use integrated video compiler: python video_compiler.py")
        print(f"4. All files are ready in: {assets['output_directory']}")


def main():
    """Command line interface"""
    import argparse
    import time
    import uuid
    
    parser = argparse.ArgumentParser(description='Create complete explainer video assets from text content')
    parser.add_argument('--no-tts', action='store_true', help='Skip TTS audio generation')
    parser.add_argument('--tts-service', choices=['gtts', 'edge_tts', 'azure', 'simple'], 
                       default='gtts', help='TTS service to use (default: gtts)')
    parser.add_argument('--lang', default='en', help='Language code for TTS (default: en)')
    parser.add_argument('--voice', default='en-US-AriaNeural', help='Voice for TTS (default: en-US-AriaNeural)')
    parser.add_argument('--no-video', action='store_true', help='Skip video compilation')
    parser.add_argument('--video-resolution', choices=['720p', '1080p', '4k'], 
                       default='720p', help='Video resolution (default: 720p)')
    parser.add_argument('--video-fps', type=int, default=30, help='Video frame rate (default: 30)')
    
    args = parser.parse_args()
    
    # Generate a job ID (timestamp-based for simplicity)
    job_id = str(int(time.time()))
    job_output_dir = Path("generated_videos") / f"job_{job_id}"
    job_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n🆔 Job ID: {job_id}")
    print(f"📁 Output directory: {job_output_dir}\n")
    
    print("=== EXPLAINER VIDEO CREATOR ===")
    print("Create complete video assets from text content")
    if not args.no_tts:
        print(f"🎵 TTS Service: {args.tts_service}")
        if args.tts_service == 'gtts':
            print(f"🌍 Language: {args.lang}")
        elif args.tts_service in ['edge_tts', 'azure']:
            print(f"🎤 Voice: {args.voice}")
    else:
        print("🎵 TTS: Disabled")
    
    if not args.no_video:
        print(f"🎬 Video Compilation: Enabled ({args.video_resolution}, {args.video_fps}fps)")
    else:
        print("🎬 Video Compilation: Disabled")
    print()
    
    # Get user text input
    print("Enter your text content (press Ctrl+D or Ctrl+Z when done):")
    print("(Or paste your content and press Enter twice)")
    
    text_lines = []
    empty_line_count = 0
    
    try:
        while True:
            line = input()
            if line.strip() == "":
                empty_line_count += 1
                if empty_line_count >= 2:  # Two empty lines = done
                    break
            else:
                empty_line_count = 0
                text_lines.append(line)
    except EOFError:
        # Ctrl+D pressed
        pass
    
    user_text = "\n".join(text_lines).strip()
    
    if not user_text:
        print("No text provided. Exiting.")
        return
    
    # Get optional parameters
    try:
        duration = int(input(f"\nTarget video duration in seconds (default: 60): ") or "60")
        segments = input("Number of segments (default: auto): ").strip()
        segments = int(segments) if segments else None
    except ValueError:
        duration = 60
        segments = None
    
    # Create video assets
    creator = ExplainerVideoCreator(output_dir=job_output_dir)
    
    # Set video compilation options
    if args.no_video:
        creator.skip_video_compilation = True
    else:
        # Configure video compiler with user preferences
        creator.video_compiler.video_width, creator.video_compiler.video_height = {
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160)
        }[args.video_resolution]
        creator.video_compiler.fps = args.video_fps
    
    result = creator.create_complete_video_assets(user_text, duration, segments, 
                                               enable_tts=not args.no_tts,
                                               tts_service=args.tts_service,
                                               tts_kwargs={'lang': args.lang, 'voice': args.voice})
    
    if result:
        print(f"\n🎉 SUCCESS! All video assets created in: {result['output_directory']}")
        sys.exit(0)
    else:
        print(f"\n💥 FAILED! Check error messages above")
        sys.exit(1)


if __name__ == '__main__':
    main()
