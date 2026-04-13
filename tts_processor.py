#!/usr/bin/env python3
"""
TTS Processor for Explainer Video Narrations
Cleans narration text and generates audio files using multiple TTS services
"""

import os
import re
import requests
import threading
from pathlib import Path
from typing import List, Dict, Tuple
import time
from dotenv import load_dotenv
try:
    import google.genai as genai
    from google.genai import types
    GENAI_NEW = True
except ImportError:
    import google.generativeai as genai
    GENAI_NEW = False
import base64
import io
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# Configure Google GenAI
if GENAI_NEW:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class TTSProcessor:
    """Process narration text and generate audio files for video segments"""
    
    def __init__(self, video_segments_dir: str = "video_segments"):
        self.video_segments_dir = Path(video_segments_dir)
        self.audio_output_dir = self.video_segments_dir / "audio"
        self.audio_output_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
        
        # TTS service configurations
        self.tts_services = {
            'gemini_tts': self._generate_with_gemini_tts
        }
        
    def clean_narration_text(self, narration_file: Path) -> Tuple[str, Dict]:
        """
        Clean narration text by removing metadata headers and extracting clean text
        
        Args:
            narration_file: Path to narration text file
            
        Returns:
            Tuple of (clean_text, metadata_dict)
        """
        with open(narration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from headers
        metadata = {}
        clean_lines = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                # Parse metadata
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.replace('#', '').strip().lower()
                    value = value.strip()
                    metadata[key] = value
            else:
                # This is actual narration text
                if line:  # Skip empty lines
                    clean_lines.append(line)
        
        clean_text = ' '.join(clean_lines)
        
        # Clean up common artifacts
        clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace
        clean_text = clean_text.strip()
        
        return clean_text, metadata
    
    def clean_all_narrations(self) -> List[Dict]:
        """
        Clean all narration files in the video segments directory
        
        Returns:
            List of cleaned narration data with metadata
        """
        print("🧹 Cleaning narration text files...")
        
        cleaned_narrations = []
        narration_files = list(self.video_segments_dir.glob("segment_*_narration.txt"))
        
        for narration_file in sorted(narration_files):
            print(f"📝 Processing: {narration_file.name}")
            
            clean_text, metadata = self.clean_narration_text(narration_file)
            
            # Extract segment number from filename
            segment_match = re.search(r'segment_(\d+)_narration', narration_file.name)
            if segment_match:
                segment_num = int(segment_match.group(1))
            else:
                segment_num = 0
            
            output_audio = str(self.audio_output_dir / f"segment_{segment_num:02d}_audio.wav")
            narration_data = {
                'segment_number': segment_num,
                'file_path': str(narration_file),
                'clean_text': clean_text,
                'metadata': metadata,
                'output_audio': output_audio
            }
            
            cleaned_narrations.append(narration_data)
            
            print(f"   ✅ Cleaned text: {clean_text[:50]}...")
        
        print(f"🎉 Cleaned {len(cleaned_narrations)} narration files")
        return cleaned_narrations
    
    def _generate_with_gemini_tts(self, text: str, output_path: str, **kwargs) -> bool:
        """Generate audio using gTTS as Gemini doesn't support TTS yet"""
        print(f"   Using Google Text-to-Speech (gTTS) for TTS generation...")
        return self._generate_with_gtts_fallback(text, output_path, **kwargs)
    
    def _generate_with_gtts_fallback(self, text: str, output_path: str, **kwargs) -> bool:
        """Fallback TTS using gTTS when Gemini TTS is not available"""
        try:
            from gtts import gTTS
            import tempfile
            
            print(f"   🔊 Using gTTS fallback for: {text[:50]}...")
            
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file first
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            try:
                tts.save(temp_file.name)
                
                # Convert to WAV using pydub
                audio = AudioSegment.from_mp3(temp_file.name)
                audio.export(output_path, format='wav')
            finally:
                # Clean up temp file
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            
            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                print(f"   ✅ gTTS fallback success: {Path(output_path).name} ({Path(output_path).stat().st_size} bytes)")
                return True
            else:
                print("   ❌ gTTS fallback: Failed to create valid audio file")
                return False
                
        except ImportError:
            print(f"   ❌ gTTS not available. Please install: pip install gtts")
            return False
        except Exception as e:
            print(f"   ❌ gTTS fallback error: {e}")
            return False
    
    def generate_audio_for_segment(
        self, narration_data: Dict, tts_service: str = 'gemini_tts', **kwargs
    ) -> bool:
        """
        Generate audio for a single narration segment with existence check
        
        Args:
            narration_data: Dictionary with segment information
            tts_service: TTS service to use ('gemini_tts')
            **kwargs: Additional arguments for TTS service
            
        Returns:
            True if successful, False otherwise
        """
        segment_num = narration_data['segment_number']
        clean_text = narration_data['clean_text']
        output_path = narration_data['output_audio']
        
        # Check if file already exists and is valid
        if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
            print(f"   ⏭️  Audio for Segment {segment_num} already exists, skipping.")
            narration_data['audio_generated'] = True
            narration_data['audio_file'] = output_path
            return True
            
        print(f"\n🎵 Generating audio for Segment {segment_num}...")
        print(f"   📝 Text: {clean_text[:80]}...")
        print(f"   🎯 Output: {Path(output_path).name}")
        
        if tts_service not in self.tts_services:
            print(f"   ❌ Unknown TTS service: {tts_service}")
            return False
        
        # Generate audio using selected service with thread lock
        with self.lock:
            success = self.tts_services[tts_service](clean_text, output_path, **kwargs)
        
        if success:
            # Update narration data with audio file info
            narration_data['audio_generated'] = True
            narration_data['audio_file'] = output_path
            narration_data['tts_service'] = tts_service
            
            # Get file size
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                narration_data['audio_file_size'] = file_size
                print(f"   📊 Audio file size: {file_size} bytes")
        
        return success
    
    def generate_all_audio(self, tts_service: str = 'gemini_tts', generate_complete: bool = False, **kwargs) -> List[Dict]:
        """
        Generate audio for all narration segments - PARALLEL VERSION
        
        Args:
            tts_service: TTS service to use
            generate_complete: Whether to generate a combined audio file of all segments
            **kwargs: Additional arguments for TTS service
            
        Returns:
            List of narration data with audio generation results
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        print(f"🎵 VERIFYING AUDIO SEGMENTS")
        print(f"=" * 50)
        print(f"TTS Service: {tts_service}")
        print(f"Output Directory: {self.audio_output_dir}")
        print()
        
        # Clean all narrations first
        cleaned_narrations = self.clean_all_narrations()
        
        if not cleaned_narrations:
            print("❌ No narration files found to process")
            return []
        
        # DEBUG: Force sequential processing for ALL services to isolate issues
        # The custom API server (147.182.254.9) crashes when hit with parallel requests
        max_workers = 1
        
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all audio generation tasks
            futures = {
                executor.submit(
                    self.generate_audio_for_segment, 
                    narration_data, 
                    tts_service, 
                    **kwargs
                ): narration_data for narration_data in cleaned_narrations
            }
            
            # Process completed tasks as they finish
            for future in as_completed(futures):
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        # Generate complete audio file only if requested
        complete_audio_success = False
        if generate_complete:
            complete_audio_success = self._generate_complete_audio(cleaned_narrations, tts_service, **kwargs)
        
        # Print summary
        print(f"\n" + "=" * 50)
        print(f"📊 AUDIO GENERATION SUMMARY")
        print(f"=" * 50)
        print(f"Total segments: {len(cleaned_narrations)}")
        print(f"Successful audio: {success_count}")
        if generate_complete:
            print(f"Complete audio: {'✅' if complete_audio_success else '❌'}")
        print(f"Output directory: {self.audio_output_dir}")
        
        return cleaned_narrations
    
    def _generate_complete_audio(self, narrations: List[Dict], tts_service: str, **kwargs) -> bool:
        """Generate a complete audio file combining all segments"""
        try:
            # Get all successful audio files
            audio_files = [n for n in narrations if n.get('audio_generated', False)]
            
            if not audio_files:
                print("❌ No audio files available for complete audio generation")
                return False
            
            # Create complete narration text
            complete_text = " ".join([n['clean_text'] for n in audio_files])
            
            # Generate complete audio
            complete_audio_path = self.audio_output_dir / "complete_narration_audio.wav"
            
            print(f"\n🎵 Generating complete narration audio...")
            print(f"   📝 Combined text length: {len(complete_text)} characters")
            print(f"   🎯 Output: {complete_audio_path.name}")
            
            success = self.tts_services[tts_service](complete_text, str(complete_audio_path), **kwargs)
            
            if success:
                file_size = complete_audio_path.stat().st_size
                print(f"   ✅ Complete audio: {complete_audio_path.name} ({file_size} bytes)")
                return True
            else:
                print(f"   ❌ Failed to generate complete audio")
                return False
                
        except Exception as e:
            print(f"❌ Error generating complete audio: {e}")
            return False
    
    def create_audio_summary(self, narrations: List[Dict]) -> str:
        """Create a summary file with audio generation results"""
        summary_file = self.audio_output_dir / "audio_generation_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Audio Generation Summary\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total segments: {len(narrations)}\n\n")
            
            f.write("## Segment Audio Files\n\n")
            for narration in narrations:
                segment_num = narration['segment_number']
                title = narration['metadata'].get('title', f'Segment {segment_num}')
                duration = narration['metadata'].get('duration', 'Unknown')
                
                f.write(f"### Segment {segment_num}: {title}\n")
                f.write(f"- **Duration**: {duration}\n")
                f.write(f"- **Text**: {narration['clean_text'][:100]}...\n")
                
                if narration.get('audio_generated'):
                    audio_file = Path(narration['audio_file']).name
                    file_size = narration.get('audio_file_size', 'Unknown')
                    tts_service = narration.get('tts_service', 'Unknown')
                    
                    f.write(f"- **Audio**: ✅ {audio_file}\n")
                    f.write(f"- **Size**: {file_size} bytes\n")
                    f.write(f"- **TTS Service**: {tts_service}\n")
                else:
                    f.write(f"- **Audio**: ❌ Failed\n")
                
                f.write("\n")
            
            # Check for complete audio
            complete_audio = self.audio_output_dir / "complete_narration_audio.wav"
            if complete_audio.exists():
                file_size = complete_audio.stat().st_size
                f.write(f"## Complete Audio\n\n")
                f.write(f"- **File**: {complete_audio.name}\n")
                f.write(f"- **Size**: {file_size} bytes\n")
                f.write(f"- **Contains**: All {len(narrations)} segments combined\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review generated audio files for quality\n")
            f.write("2. Use audio files with video editing software\n")
            f.write("3. Sync audio with background images and text overlays\n")
            f.write("4. Combine into final explainer video\n")
        
        print(f"📋 Audio summary created: {summary_file}")
        return str(summary_file)


def main():
    """Command line interface for TTS processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate audio from video narration files')
    parser.add_argument('--service', choices=['gemini_tts'], 
                       default='gemini_tts', help='TTS service to use')
    parser.add_argument('--lang', default='en', help='Language code (for gTTS)')
    parser.add_argument('--voice', default='en-US-AriaNeural', help='Voice (for Edge TTS/Azure)')
    parser.add_argument('--clean-only', action='store_true', help='Only clean text, don\'t generate audio')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = TTSProcessor()
    
    if args.clean_only:
        # Just clean the narrations
        cleaned = processor.clean_all_narrations()
        print(f"\n✅ Cleaned {len(cleaned)} narration files")
        for narration in cleaned:
            print(f"   Segment {narration['segment_number']}: {narration['clean_text'][:50]}...")
    else:
        # Generate audio
        kwargs = {}
        if args.service == 'gtts':
            kwargs['lang'] = args.lang
        elif args.service in ['edge_tts', 'azure']:
            kwargs['voice'] = args.voice
        
        narrations = processor.generate_all_audio(args.service, **kwargs)
        
        # Create summary
        if narrations:
            processor.create_audio_summary(narrations)
            print(f"\n🎉 Audio generation complete! Check {processor.audio_output_dir} for results.")


if __name__ == '__main__':
    main()