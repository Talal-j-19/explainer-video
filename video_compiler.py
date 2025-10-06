#!/usr/bin/env python3
"""
Video Compiler for Explainer Videos
Combines background images with audio segments and creates final video
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import time


class VideoCompiler:
    """Compile explainer video segments into final video"""
    
    def __init__(self, output_dir: str = "generated_videos"):
        self.output_dir = Path(output_dir) if output_dir else Path("generated_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Segments folder lives inside the job folder
        self.video_segments_dir = self.output_dir / "segments"
        self.video_segments_dir.mkdir(parents=True, exist_ok=True)
        
        # Video settings
        self.video_width = 1920
        self.video_height = 1080
        self.fps = 30
        self.video_codec = "libx264"
        self.audio_codec = "aac"
        
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_segment_duration(self, audio_file: str) -> float:
        """Get duration of audio file using FFmpeg"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                print(f"⚠️  Could not determine duration for {audio_file}, using default")
                return 10.0  # Default duration
        except Exception as e:
            print(f"⚠️  Error getting duration for {audio_file}: {e}, using default")
            return 10.0  # Default duration
    
    def compile_segment(self, segment_num: int, background_image: str, 
                       audio_file: str, output_file: str) -> bool:
        """
        Compile a single video segment
        
        Args:
            segment_num: Segment number
            background_image: Path to background image
            audio_file: Path to audio file
            output_file: Output video file path
            
        Returns:
            True if successful, False otherwise
        """
        print(f"🎬 Compiling Segment {segment_num}...")
        
        # Get audio duration
        duration = self.get_segment_duration(audio_file)
        print(f"   ⏱️  Audio duration: {duration:.2f} seconds")
        
        # Create FFmpeg command for segment
        cmd = [
            'ffmpeg', '-y',  # Overwrite output files
            '-loop', '1',     # Loop the image
            '-i', background_image,  # Input image
            '-i', audio_file,        # Input audio
            '-c:v', self.video_codec,  # Video codec
            '-c:a', self.audio_codec,  # Audio codec
            '-pix_fmt', 'yuv420p',     # Pixel format for compatibility
            '-shortest',                # End when shortest input ends
            '-t', str(duration),        # Duration limit
            '-vf', f'scale={int(self.video_width)}:{int(self.video_height)}:force_original_aspect_ratio=decrease,pad={int(self.video_width)}:{int(self.video_height)}:(ow-iw)/2:(oh-ih)/2:black',
            '-r', str(self.fps),        # Frame rate
            '-b:v', '2M',               # Video bitrate
            '-b:a', '128k',             # Audio bitrate
            output_file
        ]
        
        try:
            print(f"   🎯 Output: {Path(output_file).name}")
            print(f"   🔧 FFmpeg command: {' '.join(cmd)}")
            
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Verify output file
                if Path(output_file).exists() and Path(output_file).stat().st_size > 0:
                    file_size = Path(output_file).stat().st_size
                    print(f"   ✅ Segment {segment_num} compiled successfully ({file_size} bytes)")
                    return True
                else:
                    print(f"   ❌ Segment {segment_num} output file invalid")
                    return False
            else:
                print(f"   ❌ Segment {segment_num} compilation failed")
                print(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Segment {segment_num} compilation timed out")
            return False
        except Exception as e:
            print(f"   ❌ Segment {segment_num} compilation error: {e}")
            return False
    
    def compile_all_segments(self) -> List[str]:
        """
        Compile all video segments
        
        Returns:
            List of compiled segment video files
        """
        print("🎬 COMPILING ALL VIDEO SEGMENTS")
        print("=" * 50)
        
        # Check FFmpeg availability
        if not self.check_ffmpeg():
            print("❌ FFmpeg not found! Please install FFmpeg first.")
            print("   Download from: https://ffmpeg.org/download.html")
            return []
        
        # Load video script
        script_file = self.video_segments_dir / "video_script.json"
        if not script_file.exists():
            print("❌ Video script not found! Run create_explainer_video.py first.")
            return []
        
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script = json.load(f)
        except Exception as e:
            print(f"❌ Error loading video script: {e}")
            return []
        
        # Get segments
        segments = script.get('segments', [])
        if not segments:
            print("❌ No segments found in video script")
            return []
        
        print(f"📋 Found {len(segments)} segments to compile")
        
        # Compile each segment
        compiled_segments = []
        success_count = 0
        
        for segment in segments:
            segment_num = segment['segment_number']
            
            # Get file paths
            background_image = segment.get('background_image', '')
            audio_file = self.video_segments_dir / "audio" / f"segment_{segment_num:02d}_audio.mp3"
            
            if not background_image or not Path(background_image).exists():
                print(f"   ❌ Segment {segment_num}: Background image not found")
                continue
                
            if not audio_file.exists():
                print(f"   ❌ Segment {segment_num}: Audio file not found")
                continue
            
            # Output file (always in job folder)
            output_file = self.output_dir / f"segment_{segment_num:02d}_video.mp4"
            
            # Compile segment
            if self.compile_segment(segment_num, background_image, str(audio_file), str(output_file)):
                compiled_segments.append(str(output_file))
                success_count += 1
            else:
                print(f"   ❌ Segment {segment_num} compilation failed")
        
        print(f"\n📊 Segment compilation summary:")
        print(f"   Total segments: {len(segments)}")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {len(segments) - success_count}")
        
        return compiled_segments
    
    def create_video_list_file(self, video_files: List[str]) -> str:
        """Create a text file listing all video files for FFmpeg concatenation"""
        list_file = self.output_dir / "video_list.txt"
        
        with open(list_file, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                # Use absolute paths to avoid path issues
                video_path = Path(video_file).resolve()
                f.write(f"file '{video_path}'\n")
        
        return str(list_file)
    
    def concatenate_videos(self, video_files: List[str], output_file: str) -> bool:
        """
        Concatenate all video segments into final video
        
        Args:
            video_files: List of video file paths
            output_file: Final output video path
            
        Returns:
            True if successful, False otherwise
        """
        if not video_files:
            print("❌ No video files to concatenate")
            return False
        
        print(f"\n🎬 CONCATENATING {len(video_files)} VIDEO SEGMENTS")
        print("=" * 50)
        print(f"🎯 Final output: {Path(output_file).name}")
        
        # Create video list file
        list_file = self.create_video_list_file(video_files)
        print(f"📋 Created video list file: {Path(list_file).name}")
        
        # FFmpeg concatenation command
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-f', 'concat',   # Use concat demuxer
            '-safe', '0',     # Allow unsafe file paths
            '-i', list_file,  # Input list file
            '-c', 'copy',      # Copy streams without re-encoding
            output_file
        ]
        
        try:
            print("🔧 Running FFmpeg concatenation...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                if Path(output_file).exists() and Path(output_file).stat().st_size > 0:
                    file_size = Path(output_file).stat().st_size
                    print(f"✅ Video concatenation successful!")
                    print(f"   📁 Output file: {Path(output_file).name}")
                    print(f"   📊 File size: {file_size} bytes")
                    
                    # Clean up list file
                    try:
                        os.remove(list_file)
                        print(f"   🧹 Cleaned up temporary files")
                    except:
                        pass
                    
                    return True
                else:
                    print(f"❌ Output file invalid after concatenation")
                    return False
            else:
                print(f"❌ Video concatenation failed")
                print(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Video concatenation timed out")
            return False
        except Exception as e:
            print(f"❌ Video concatenation error: {e}")
            return False
    
    def compile_complete_video(self) -> Optional[str]:
        """
        Compile complete explainer video from all segments
        
        Returns:
            Path to final video file if successful, None otherwise
        """
        print("🚀 COMPILING COMPLETE EXPLAINER VIDEO")
        print("=" * 60)
        
        # Step 1: Compile all segments
        compiled_segments = self.compile_all_segments()
        
        if not compiled_segments:
            print("❌ No segments compiled successfully")
            return None
        
        # Step 2: Concatenate into final video (always in job folder)
        timestamp = int(time.time())
        final_video = self.output_dir / f"explainer_video_{timestamp}.mp4"
        
        if self.concatenate_videos(compiled_segments, str(final_video)):
            print(f"\n🎉 COMPLETE VIDEO COMPILED SUCCESSFULLY!")
            print(f"📁 Final video: {final_video}")
            print(f"📊 Total segments: {len(compiled_segments)}")
            return str(final_video)
        else:
            print(f"\n❌ Video compilation failed")
            return None
    
    def create_compilation_summary(self, video_files: List[str], final_video: Optional[str]) -> str:
        """Create a summary of the video compilation process"""
        summary_file = self.output_dir / "video_compilation_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Video Compilation Summary\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total segments: {len(video_files)}\n\n")
            
            f.write("## Compiled Segments\n\n")
            for i, video_file in enumerate(video_files, 1):
                file_path = Path(video_file)
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    f.write(f"### Segment {i}\n")
                    f.write(f"- **File**: {file_path.name}\n")
                    f.write(f"- **Size**: {file_size} bytes\n")
                    f.write(f"- **Status**: ✅ Compiled\n\n")
                else:
                    f.write(f"### Segment {i}\n")
                    f.write(f"- **File**: {file_path.name}\n")
                    f.write(f"- **Status**: ❌ Missing\n\n")
            
            if final_video:
                final_path = Path(final_video)
                if final_path.exists():
                    file_size = final_path.stat().st_size
                    f.write("## Final Video\n\n")
                    f.write(f"- **File**: {final_path.name}\n")
                    f.write(f"- **Size**: {file_size} bytes\n")
                    f.write(f"- **Status**: ✅ Complete\n\n")
                else:
                    f.write("## Final Video\n\n")
                    f.write(f"- **Status**: ❌ Failed\n\n")
            else:
                f.write("## Final Video\n\n")
                f.write(f"- **Status**: ❌ Not created\n\n")
            
            f.write("## Video Settings\n\n")
            f.write(f"- **Resolution**: {self.video_width}x{self.video_height}\n")
            f.write(f"- **Frame Rate**: {self.fps} fps\n")
            f.write(f"- **Video Codec**: {self.video_codec}\n")
            f.write(f"- **Audio Codec**: {self.audio_codec}\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the compiled video for quality\n")
            f.write("2. Check audio synchronization with visuals\n")
            f.write("3. Use in your video editing software if needed\n")
            f.write("4. Share or upload your explainer video!\n")
        
        print(f"📋 Compilation summary created: {summary_file}")
        return str(summary_file)


def main():
    """Command line interface for video compilation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compile explainer video from segments')
    parser.add_argument('--output-dir', default='generated_videos', 
                       help='Output directory for compiled videos')
    parser.add_argument('--resolution', choices=['720p', '1080p', '4k'], 
                       default='1080p', help='Video resolution')
    parser.add_argument('--fps', type=int, default=30, 
                       help='Frame rate (default: 30)')
    parser.add_argument('--segments-only', action='store_true',
                       help='Only compile segments, don\'t concatenate')
    
    args = parser.parse_args()
    
    # Set resolution
    resolutions = {
        '720p': (1280, 720),
        '1080p': (1920, 1080),
        '4k': (3840, 2160)
    }
    
    width, height = resolutions[args.resolution]
    
    print("=== VIDEO COMPILER ===")
    print(f"Resolution: {args.resolution} ({width}x{height})")
    print(f"Frame Rate: {args.fps} fps")
    print(f"Output Directory: {args.output_dir}")
    print()
    
    # Initialize compiler
    compiler = VideoCompiler()
    compiler.video_width = width
    compiler.video_height = height
    compiler.fps = args.fps
    compiler.output_dir = Path(args.output_dir)
    
    if args.segments_only:
        # Only compile segments
        compiled_segments = compiler.compile_all_segments()
        if compiled_segments:
            print(f"\n✅ Compiled {len(compiled_segments)} segments")
            print(f"📁 Check {compiler.output_dir} for results")
        else:
            print(f"\n❌ No segments compiled successfully")
    else:
        # Compile complete video
        final_video = compiler.compile_complete_video()
        if final_video:
            print(f"\n🎉 Video compilation complete!")
            print(f"📁 Final video: {final_video}")
        else:
            print(f"\n❌ Video compilation failed")


if __name__ == '__main__':
    main()
