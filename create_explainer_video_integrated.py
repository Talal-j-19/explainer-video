#!/usr/bin/env python3
"""
Explainer Video with Integrated Template-Based Infographics
Main entry point that uses the new integrated image generator

This script replaces the need for external API calls by directly using
the Node.js generateInfographicV2Service for infographic generation.

Usage:
    python create_explainer_video_integrated.py "Your topic here"
"""

import os
import asyncio
import sys
import logging
from pathlib import Path

# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GCLOUD_PYTHON_LOGGING_LEVEL'] = 'ERROR'
logging.getLogger('grpc').setLevel(logging.ERROR)
logging.getLogger('googleapis.gapic').setLevel(logging.ERROR)
import json
import time
from dotenv import load_dotenv

# Load environment variables from main directory
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"⚠️ .env file not found at {env_path}")

# Import the integrated image generator
from integrated_image_generator import IntegratedImageGenerator

# Import other required modules
from create_explainer_video import ExplainerVideoCreator
from tts_processor import TTSProcessor
from video_compiler import VideoCompiler
from job_manager import InfographicJobManager


class IntegratedExplainerVideoCreator(ExplainerVideoCreator):
    """
    Enhanced ExplainerVideoCreator that uses template-based infographics
    instead of external API calls
    """
    
    def __init__(self, use_integrated: bool = True):
        """
        Initialize with integrated image generation
        
        Args:
            use_integrated: Use the new template-based system (default: True)
        """
        super().__init__()
        self.use_integrated = use_integrated
        self.image_generator = None
        
        if use_integrated:
            self.image_generator = IntegratedImageGenerator(
                output_dir="video_segments",
                use_content_only=True
            )
            print("🔗 Using integrated template-based infographic system")
        else:
            print("⚠️ Using legacy external API")
    
    async def generate_video_with_integrated_images(
        self,
        prompt: str,
        target_duration: int = 60,
        output_dir: str = "generated_videos"
    ) -> dict:
        """
        Generate complete explainer video using integrated infographics
        
        Args:
            prompt: Topic for the explainer video
            target_duration: Target video duration in seconds
            output_dir: Output directory for final video
            
        Returns:
            Dictionary with video metadata and file paths
        """
        print("\n" + "="*70)
        print("🎬 INTEGRATED EXPLAINER VIDEO GENERATION")
        print("="*70)
        
        start_time = time.time()
        
        try:
            # Step 1: Create script
            print("\n1️⃣ CREATING VIDEO SCRIPT")
            print("-" * 70)
            
            job_id = int(time.time())
            job_dir = Path(output_dir) / f"job_{job_id}"
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate script using video_generator
            print(f"📝 Generating script from prompt: {prompt[:50]}...")
            result = self.video_generator.generate_explainer_video_plan(
                prompt,
                target_duration=target_duration
            )
            
            if not result:
                raise Exception("Failed to generate video script")
            
            script_path = result['script_path']
            script = result['script']
            print(f"✅ Script created: {script_path}")
            
            # Copy script to job directory
            import shutil
            final_script_path = job_dir / "video_script.json"
            shutil.copy(script_path, final_script_path)
            script_path = final_script_path
            
            # Step 1.5: Generate opening and closing pages
            print("\n1️⃣.5️⃣ GENERATING PROFESSIONAL OPENING & CLOSING PAGES")
            print("-" * 70)
            
            # Load script to get segments for closing page summary
            with open(script_path, 'r') as f:
                script_data = json.load(f)
            
            # Get content segments
            if isinstance(script_data, dict) and 'segments' in script_data:
                segments = script_data['segments']
            elif isinstance(script_data, list):
                segments = script_data
            else:
                segments = []
            
            opening_page = await self.image_generator.generate_opening_page(prompt, str(job_dir))
            closing_page = await self.image_generator.generate_closing_page_with_summary(prompt, str(job_dir), segments)
            
            # Load script and add opening/closing segments
            with open(script_path, 'r') as f:
                script_data = json.load(f)
            
            # Get content segments
            if isinstance(script_data, dict) and 'segments' in script_data:
                segments = script_data['segments']
            elif isinstance(script_data, list):
                segments = script_data
            else:
                segments = []
            
            # Create opening segment
            opening_segment = {
                'segment_number': 0,
                'title': 'Introduction',
                'narration_text': f'Welcome. In this video, we explore {prompt}. Let\'s dive in.',
                'duration': 4,
                'image_prompt': 'Professional opening title',
                'background_image': str(opening_page) if opening_page else ''
            }
            
            # Create closing segment
            closing_segment = {
                'segment_number': len(segments) + 1,
                'title': 'Conclusion',
                'narration_text': f'Thank you for learning about {prompt}.',
                'duration': 2,
                'image_prompt': 'Professional closing thank you',
                'background_image': str(closing_page) if closing_page else ''
            }
            
            # Renumber content segments
            for idx, segment in enumerate(segments, 1):
                segment['segment_number'] = idx
            
            # Build full segments list
            full_segments = [opening_segment] + segments + [closing_segment]
            
            # Update script
            if isinstance(script_data, dict):
                script_data['segments'] = full_segments
            else:
                script_data = full_segments
            
            # Save updated script
            with open(script_path, 'w') as f:
                json.dump(script_data, f, indent=2)
            print(f"✅ Added opening and closing segments to script")
            
            # Create narration files from all segments
            print("📝 Extracting narration from script (including opening/closing)...")
            
            for segment in full_segments:
                if isinstance(segment, dict):
                    segment_num = segment.get('segment_number', 0)
                    narration_text = segment.get('narration_text', '')
                    
                    if narration_text:
                        narration_file = job_dir / f"segment_{segment_num:02d}_narration.txt"
                        with open(narration_file, 'w') as f:
                            f.write(narration_text)
                        print(f"✅ Created narration file: segment_{segment_num:02d}_narration.txt")
            
            # Step 2: Generate images using integrated system
            print("\n2️⃣ GENERATING INFOGRAPHICS (Template-Based V2)")
            print("-" * 70)
            
            if self.use_integrated and self.image_generator:
                images_success = await self.image_generator.generate_images_for_script(
                    str(script_path),
                    topic=prompt  # Pass topic for consistent color scheme
                )
                
                if not images_success:
                    print("⚠️ Some images failed, continuing...")
            else:
                print("⚠️ Integrated mode disabled")
                images_success = False
            
            # Step 3: Generate audio
            print("\n3️⃣ GENERATING AUDIO")
            print("-" * 70)
            
            tts_processor = TTSProcessor(video_segments_dir=str(job_dir))
            audio_results = tts_processor.generate_all_audio(tts_service='gtts')
            audio_success = len(audio_results) > 0
            
            if not audio_success:
                print("⚠️ Audio generation had issues")
            
            # Step 4: Update script with image paths and prepare for compilation
            print("\n4️⃣ PREPARING FOR VIDEO COMPILATION")
            print("-" * 70)
            
            # Ensure segments directory exists for VideoCompiler
            segments_dir = job_dir / "segments"
            segments_dir.mkdir(exist_ok=True)
            
            # Copy audio files to segments/audio directory
            audio_segments_dir = segments_dir / "audio"
            audio_segments_dir.mkdir(exist_ok=True)
            
            audio_dir = job_dir / "audio"
            if audio_dir.exists():
                for audio_file in audio_dir.glob("segment_*.mp3"):
                    shutil.copy(audio_file, audio_segments_dir / audio_file.name)
                print(f"✅ Copied audio files to segments/audio/")
            
            # Copy background images to segments directory
            segments_bg_dir = segments_dir / "backgrounds"
            segments_bg_dir.mkdir(exist_ok=True)
            
            # Copy all background PNG files from video_segments directory
            video_segments_path = Path("video_segments")
            if video_segments_path.exists():
                for bg_file in video_segments_path.glob("segment_*_background.png"):
                    shutil.copy(bg_file, segments_bg_dir / bg_file.name)
            
            # Copy opening and closing page images
            if (job_dir / "opening_page.png").exists():
                shutil.copy(job_dir / "opening_page.png", segments_bg_dir / "segment_00_background.png")
                print(f"✅ Copied opening page image")
            
            if (job_dir / "closing_page.png").exists():
                closing_num = len(full_segments) - 1  # Last segment index (0-based)
                shutil.copy(job_dir / "closing_page.png", segments_bg_dir / f"segment_{closing_num:02d}_background.png")
                print(f"✅ Copied closing page image to segment_{closing_num:02d}_background.png")
            
            # Copy script and images to segments directory
            segments_script = segments_dir / "video_script.json"
            shutil.copy(script_path, segments_script)
            
            # Update script with image paths
            with open(segments_script, 'r') as f:
                script_for_compiler = json.load(f)
            
            # Handle both dict and list formats
            if isinstance(script_for_compiler, dict) and 'segments' in script_for_compiler:
                segments_list = script_for_compiler['segments']
            elif isinstance(script_for_compiler, list):
                segments_list = script_for_compiler
            else:
                segments_list = []
            
            # Update segment background images with absolute paths
            updated_segments = []
            for segment in segments_list:
                if isinstance(segment, dict):
                    segment_num = segment.get('segment_number', 0)
                    image_path = segments_bg_dir / f"segment_{segment_num:02d}_background.png"
                    segment['background_image'] = str(image_path.resolve())
                    updated_segments.append(segment)
            
            # Save updated script with image paths
            with open(segments_script, 'w') as f:
                if isinstance(script_for_compiler, dict):
                    script_for_compiler['segments'] = updated_segments
                    json.dump(script_for_compiler, f, indent=2)
                else:
                    json.dump(updated_segments, f, indent=2)
            
            print(f"✅ Prepared script with image paths: {segments_script}")
            
            # Step 5: Compile video
            print("\n5️⃣ COMPILING VIDEO")
            print("-" * 70)
            
            video_compiler = VideoCompiler(output_dir=str(job_dir))
            final_video = video_compiler.compile_complete_video()
            
            # Step 6: Summary
            elapsed = time.time() - start_time
            
            print("\n" + "="*70)
            print("✅ VIDEO GENERATION COMPLETE")
            print("="*70)
            
            result = {
                "success": final_video is not None,
                "job_id": job_id,
                "job_dir": str(job_dir),
                "script": str(script_path),
                "final_video": final_video,
                "total_time": elapsed,
                "using_integrated": self.use_integrated
            }
            
            if final_video:
                print(f"🎉 Video saved: {final_video}")
                print(f"📊 Rendering system: {'Template-Based V2' if self.use_integrated else 'External API'}")
                print(f"⏱️ Total time: {elapsed:.1f} seconds")
            else:
                print("❌ Video compilation failed")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "using_integrated": self.use_integrated
            }


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create explainer video with integrated template-based infographics'
    )
    parser.add_argument(
        'prompt',
        help='Topic for the explainer video'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Target video duration in seconds (default: 60)'
    )
    parser.add_argument(
        '--output-dir',
        default='generated_videos',
        help='Output directory (default: generated_videos)'
    )
    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Use legacy external API instead of integrated system'
    )
    
    args = parser.parse_args()
    
    # Create integrated creator
    creator = IntegratedExplainerVideoCreator(use_integrated=not args.legacy)
    
    # Generate video
    result = await creator.generate_video_with_integrated_images(
        prompt=args.prompt,
        target_duration=args.duration,
        output_dir=args.output_dir
    )
    
    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python create_explainer_video_integrated.py 'Your topic'")
        print("       python create_explainer_video_integrated.py 'AI in Healthcare' --duration 90")
        sys.exit(1)
    
    asyncio.run(main())
