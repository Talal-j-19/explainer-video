#!/usr/bin/env python3
"""
Video Explainer Generator
Takes text content and creates video segments with generated background images and text overlays
"""

import os
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Suppress gRPC warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GCLOUD_PYTHON_LOGGING_LEVEL'] = 'ERROR'
logging.getLogger('grpc').setLevel(logging.ERROR)
logging.getLogger('googleapis.gapic').setLevel(logging.ERROR)


class VideoExplainerGenerator:
    """Generate explainer video segments from text content"""
    
    def __init__(self, output_dir=None):
        # Load environment variables from parent directory
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY1")
        if not api_key:
            raise Exception("GOOGLE_API_KEY or API_KEY1 environment variable not set.")
        genai.configure(api_key=api_key)
        
        # Create output directory
        self.output_dir = Path(output_dir) if output_dir else Path("video_segments")
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_text_for_video(self, text_content, target_duration=60, segments_count=None):
        """
        Analyze text and break it down into video segments with image prompts

        Args:
            text_content: The input text to analyze
            target_duration: Target video duration in seconds
            segments_count: Number of segments (auto-calculated if None)

        Returns:
            List of video segments with content, timing, and image prompts
        """
        print("🔍 Analyzing text content for video segments...")

        # Auto-calculate segments if not provided
        # Reserve 7 seconds for opening (4s) and closing (3s) pages
        content_duration = max(10, target_duration - 7)
        
        if segments_count is None:
            # Aim for 5-6 seconds per segment
            segments_count = max(3, min(15, content_duration // 5))

        # Calculate target duration per segment
        seconds_per_segment = content_duration // segments_count
        
        system_prompt = f"""
        You are an expert video script writer and visual content strategist. Your task is to analyze text content and create structured video segments with detailed image generation prompts.

        CRITICAL: You must respond with ONLY a valid JSON array. No explanations, no markdown, no extra text.

        Required JSON format - each segment must have these exact fields:
        - segment_number: Integer (1, 2, 3...)
        - title: String (short, descriptive title - max 5 words)
        - narration_text: String (CONCISE text for TTS - MAXIMUM 10-12 words, approximately {seconds_per_segment} seconds when spoken)
        - key_points: Array of strings (main concepts to highlight)
        - image_prompt: String (detailed prompt for AI image generation)
        - text_overlay: String (short text for on-screen display - max 3 words)
        - duration_seconds: Integer (target {seconds_per_segment} seconds per segment)

        CRITICAL NARRATION CONSTRAINTS:
        - Each narration_text MUST be 10-12 words maximum
        - At normal speaking pace (150 words/min), this creates ~{seconds_per_segment} second audio
        - Keep sentences SHORT and PUNCHY
        - Focus on ONE key concept per segment
        - Total video content must be exactly {content_duration} seconds

        EXAMPLE OUTPUT FORMAT:
        [
          {{
            "segment_number": 1,
            "title": "Introduction to AI",
            "narration_text": "Artificial intelligence is transforming how we work and live.",
            "key_points": ["AI transformation", "workplace impact", "daily life"],
            "image_prompt": "Modern office scene with AI-related visual elements: computer screens showing data analytics, robotic arm, neural network diagrams, and productivity charts. Professional blue and white color scheme with clear areas for text overlays at top and bottom",
            "text_overlay": "AI TRANSFORMATION",
            "duration_seconds": {seconds_per_segment}
          }}
        ]
        
        NOTE: The example narration "Artificial intelligence is transforming how we work and live" is exactly 11 words - this is the MAXIMUM length.

        For image_prompt, create detailed, specific prompts for INFORMATIVE explainer video images:
        - Describe specific visual elements that represent the content (icons, diagrams, charts, illustrations)
        - Include relevant visual metaphors, infographics, or conceptual representations
        - Specify content-related elements (e.g., "solar panels and growth charts" for renewable energy)
        - Professional, educational illustration style
        - Clear visual storytelling that matches the narration
        - Informative rather than just decorative backgrounds

        IMPORTANT: Return ONLY the JSON array, nothing else. No ```json``` markers, no explanations.
        """

        user_prompt = {
            "task": "analyze_text_for_video_segments",
            "text_content": text_content,
            "segments_count": segments_count,
            "target_duration": content_duration,
            "seconds_per_segment": seconds_per_segment,
            "requirements": [
                "Create logical, flowing segments",
                "Each segment covers one main concept",
                f"CRITICAL: Narration MUST be {seconds_per_segment} seconds (10-12 words maximum)",
                "Include detailed image generation prompts",
                "Professional, educational tone",
                f"Total content duration MUST be exactly {content_duration} seconds"
            ]
        }

        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 4096,
            }
        )

        response = model.generate_content(json.dumps(user_prompt, indent=2))
        result = response.text.strip()

        print(f"🔍 Raw response length: {len(result)} characters")

        # Clean up JSON response - be more aggressive
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

        # Find the JSON array boundaries
        start_bracket = result.find('[')
        end_bracket = result.rfind(']')

        if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
            # Extract only the JSON array part
            result = result[start_bracket:end_bracket + 1]

        # Clean up common AI response issues
        import re

        # Remove any standalone words that appear between JSON elements
        # This handles cases like "Tapi" appearing in the middle
        lines = result.split('\n')
        clean_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip lines that are just random words (not JSON syntax)
            if stripped and not any(char in stripped for char in '{}[]":,'):
                # If it's a short alphabetic string, it's probably stray text
                if len(stripped) < 20 and stripped.replace(' ', '').isalpha():
                    print(f"🧹 Removing stray text: '{stripped}'")
                    continue
            clean_lines.append(line)

        result = '\n'.join(clean_lines)

        try:
            segments = json.loads(result)
            print(f"✅ Created {len(segments)} video segments with image prompts")
            return segments
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing segments JSON: {e}")
            print(f"Cleaned response preview: {result[:300]}...")

            # Try additional fixes
            try:
                # Remove trailing commas and fix common issues
                fixed_result = re.sub(r',\s*}', '}', result)
                fixed_result = re.sub(r',\s*]', ']', fixed_result)
                # Fix missing commas between objects
                fixed_result = re.sub(r'}\s*{', '},{', fixed_result)
                # Fix incomplete strings
                fixed_result = re.sub(r'"([^"]*?)(\n|$)', r'"\1"', fixed_result)

                segments = json.loads(fixed_result)
                print(f"✅ Fixed JSON and created {len(segments)} segments")
                return segments
            except json.JSONDecodeError as e2:
                print(f"❌ Could not fix JSON: {e2}")
                
                # Last resort: try to extract complete objects from the partial JSON
                try:
                    # Find all complete JSON objects
                    objects = []
                    depth = 0
                    current_obj = ""
                    
                    for char in result:
                        if char == '{':
                            if depth == 0:
                                current_obj = "{"
                            else:
                                current_obj += char
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            current_obj += char
                            if depth == 0 and current_obj:
                                try:
                                    obj = json.loads(current_obj)
                                    objects.append(obj)
                                except:
                                    pass
                                current_obj = ""
                        else:
                            if depth > 0:
                                current_obj += char
                    
                    if objects and len(objects) >= 3:
                        print(f"✅ Extracted {len(objects)} partial segments from malformed response")
                        return objects
                except Exception as e3:
                    pass
                
                # Final fallback: Generate a basic script structure
                print(f"⚠️  Falling back to basic segment generation")
                try:
                    segments = self._generate_basic_segments(text_content, segments_count, seconds_per_segment)
                    print(f"✅ Generated {len(segments)} basic segments")
                    return segments
                except:
                    print(f"Final attempt - showing problematic area:")
                    print(result[max(0, len(result)//2-100):len(result)//2+100])
                    return None
    
    def enhance_single_prompt(self, original_prompt):
        """
        Enhance a single image prompt to create informative, content-specific images with text placeholders

        Args:
            original_prompt: Basic image prompt

        Returns:
            Enhanced prompt string for informative explainer images
        """
        if not original_prompt:
            return original_prompt

        enhancement_template = f"""
        Create an informative explainer video html code that visually represents the content with designated text areas.

        CONTENT TO VISUALIZE:
        {original_prompt}

        VISUAL REQUIREMENTS:
        - 16:9 aspect ratio (1920x1080 pixels)
        - Informative and educational illustration style
        - Clear visual representation of the concept/topic
        - Include relevant icons, diagrams, charts, or illustrations
        - Professional business/educational aesthetic
        - Modern, clean, engaging design

        TEXT PLACEHOLDER AREAS (CRITICAL):
        - Reserve the TOP 20% of the image for main title text overlay
        - Reserve the BOTTOM 15% for subtitle/key points text
        - These areas should have solid color backgrounds or subtle gradients
        - High contrast between text areas and visual content for readability
        - Text areas should be clearly defined rectangular spaces
        - Avoid placing important visual elements in text areas

        CONTENT-SPECIFIC ELEMENTS:
        - Use visual metaphors, icons, or diagrams related to the topic
        - Include relevant infographic elements (charts, arrows, progress bars)
        - Use colors that match the content theme and mood
        - Create visual hierarchy that supports the narrative
        - Show processes, comparisons, or data visualization when relevant

        STYLE GUIDELINES:
        - Avoid any text or typography in the image itself
        - Professional, corporate presentation style
        - Suitable for business/educational explainer videos
        - Clean, modern illustration or infographic style
        - Engaging but not distracting from text overlays
        - Use consistent color palette throughout

        The html should tell the story visually while providing clear, uncluttered spaces for text overlays.
        """

        return enhancement_template.strip()

    def generate_enhanced_prompts(self, segments):
        """
        Enhance image prompts for better generation quality

        Args:
            segments: List of video segments with basic html prompts

        Returns:
            Enhanced segments with improved html prompts
        """
        print("🎨 Enhancing html prompts for better generation...")

        # Simple enhancement - just enhance the prompts without complex AI calls
        enhanced_segments = []

        for segment in segments:
            enhanced_segment = segment.copy()  # Copy the original segment

            # Enhance the image prompt
            original_prompt = segment.get('image_prompt', '')
            enhanced_prompt = self.enhance_single_prompt(original_prompt)
            enhanced_segment['image_prompt'] = enhanced_prompt

            enhanced_segments.append(enhanced_segment)

        print(f"✅ Enhanced image prompts for {len(enhanced_segments)} segments")
        return enhanced_segments
    
    def create_video_script(self, segments):
        """
        Create a comprehensive video script with all segments

        Args:
            segments: List of video segments with image prompts

        Returns:
            Dictionary with complete video script data
        """
        print("📝 Creating comprehensive video script...")

        # Enhance image prompts first
        enhanced_segments = self.generate_enhanced_prompts(segments)

        total_duration = sum(seg.get('duration_seconds', 6) for seg in enhanced_segments)

        script = {
            "video_metadata": {
                "total_segments": len(enhanced_segments),
                "estimated_duration": total_duration,
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "format": "explainer_video",
                "generation_method": "gemini_with_separate_prompts"
            },
            "segments": []
        }

        for i, segment in enumerate(enhanced_segments, 1):
            # Prepare image path (will be generated later by ImageGenerator)
            image_path = str(self.output_dir / f"segment_{i:02d}_background.png")

            segment_data = {
                "segment_number": i,
                "title": segment.get('title', f'Segment {i}'),
                "narration_text": segment.get('narration_text', ''),
                "text_overlay": segment.get('text_overlay', ''),
                "key_points": segment.get('key_points', []),
                "image_prompt": segment.get('image_prompt', ''),
                "duration_seconds": segment.get('duration_seconds', 6),
                "background_image": image_path,
                "timing": {
                    "start_time": sum(seg.get('duration_seconds', 6) for seg in enhanced_segments[:i-1]),
                    "end_time": sum(seg.get('duration_seconds', 6) for seg in enhanced_segments[:i])
                }
            }

            script["segments"].append(segment_data)

        return script
    
    def save_script(self, script, filename="video_script.json"):
        """Save the video script to a JSON file"""
        script_path = self.output_dir / filename
        
        with open(script_path, 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Video script saved: {script_path}")
        return str(script_path)
    
    def generate_explainer_video_plan(self, text_content, target_duration=60, segments_count=None):
        """
        Main method to generate complete explainer video plan
        
        Args:
            text_content: Input text to convert to video
            target_duration: Target video duration in seconds
            segments_count: Number of segments (auto-calculated if None)
        
        Returns:
            Dictionary with complete video plan
        """
        print("🚀 EXPLAINER VIDEO GENERATOR")
        print("=" * 50)
        print(f"Target duration: {target_duration} seconds")
        print(f"Text length: {len(text_content)} characters")
        print()
        
        # Step 1: Analyze text and create segments
        segments = self.analyze_text_for_video(text_content, target_duration, segments_count)
        if not segments:
            return None
        
        # Step 2: Create comprehensive script with images
        script = self.create_video_script(segments)
        
        # Step 3: Save script
        script_path = self.save_script(script)
        
        # Step 4: Print summary
        self.print_summary(script)
        
        return {
            "script": script,
            "script_path": script_path,
            "output_directory": str(self.output_dir)
        }
    
    def print_summary(self, script):
        """Print a summary of the generated video plan"""
        print("\n" + "=" * 50)
        print("📊 VIDEO PLAN SUMMARY")
        print("=" * 50)
        
        metadata = script["video_metadata"]
        print(f"Total segments: {metadata['total_segments']}")
        print(f"Estimated duration: {metadata['estimated_duration']} seconds")
        print(f"Output directory: {self.output_dir}")
        print()
        
        print("📋 SEGMENTS:")
        for segment in script["segments"]:
            print(f"\n🎬 Segment {segment['segment_number']}: {segment['title']}")
            print(f"   ⏱️  Duration: {segment['duration_seconds']}s")
            print(f"   🗣️  Narration: {segment['narration_text'][:80]}...")
            print(f"   📝 Text overlay: {segment['text_overlay']}")
            print(f"   🖼️  Background: {segment['background_image']}")
        
        print(f"\n🎯 Next steps:")
        print(f"1. Review the generated script: {self.output_dir}/video_script.json")
        print(f"2. Generate actual background images (replace placeholders)")
        print(f"3. Use TTS to generate narration audio")
        print(f"4. Combine images, text overlays, and audio into video")


def main():
    """Command line interface"""
    print("=== EXPLAINER VIDEO GENERATOR ===")
    print("Provide your text content to create video segments with background images")
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
    
    # Generate video plan
    generator = VideoExplainerGenerator()
    result = generator.generate_explainer_video_plan(user_text, duration, segments)
    
    if result:
        print(f"\n🎉 SUCCESS! Video plan generated in: {result['output_directory']}")
    else:
        print(f"\n💥 FAILED! Check error messages above")


if __name__ == '__main__':
    main()
