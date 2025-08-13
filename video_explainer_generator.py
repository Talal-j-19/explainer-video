#!/usr/bin/env python3
"""
Video Explainer Generator
Takes text content and creates video segments with generated background images and text overlays
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai


class VideoExplainerGenerator:
    """Generate explainer video segments from text content"""
    
    def __init__(self, output_dir=None):
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise Exception("GOOGLE_API_KEY environment variable not set.")
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

        # Auto-calculate segments if not provided (aim for 8-12 seconds per segment)
        if segments_count is None:
            segments_count = max(3, min(10, target_duration // 8))

        system_prompt = """
        You are an expert infographic designer and educational content strategist. Your task is to create coordinated image-text pairs for explainer videos.

        CRITICAL: You must respond with ONLY a valid JSON array. No explanations, no markdown, no extra text.

        Required JSON format - each segment must have these exact fields:
        - segment_number: Integer (1, 2, 3...)
        - title: String (short, descriptive title)
        - narration_text: String (conversational text for TTS, 1-2 sentences)
        - key_points: Array of strings (main concepts to highlight)
        - image_prompt: String (detailed prompt for coordinated infographic with empty placeholders)
        - text_overlay: String (detailed structured text that maps to image placeholders)
        - duration_seconds: Integer (8-12 seconds per segment)

        CRITICAL DESIGN COORDINATION:
        The image_prompt and text_overlay must work together as a coordinated infographic system.

        For image_prompt, create infographics with SPECIFIC EMPTY PLACEHOLDERS:
        - Light colors (whites, light blues, soft greens, pastels)
        - Specific numbered or positioned empty boxes/areas for text
        - Visual elements that support the content (icons, arrows, diagrams)
        - Clear structure (flowcharts, step diagrams, comparison layouts)
        - Professional, clean infographic style
        - NO TEXT in the image itself - only empty placeholders

        For text_overlay, create DETAILED STRUCTURED CONTENT that fills those placeholders:
        - NOT just titles - use full sentences, lists, step-by-step explanations
        - Content that maps directly to the empty areas in the image
        - Structured format: numbered lists, bullet points, process steps
        - Educational and informative text that explains the concept

        EXAMPLE OUTPUT FORMAT:
        [
          {
            "segment_number": 1,
            "title": "AI Benefits in Business",
            "narration_text": "Artificial intelligence delivers measurable benefits across multiple business areas.",
            "key_points": ["efficiency gains", "cost reduction", "decision making"],
            "image_prompt": "Light blue and white infographic layout with 3 empty rectangular boxes arranged vertically on the right side, connected by arrows. Left side shows simple business icons (office building, gears, chart). Clean, minimal design with soft colors and plenty of white space.",
            "text_overlay": "1. Automates repetitive tasks and increases efficiency by 40%\n2. Reduces operational costs through smart resource allocation\n3. Improves decision-making with data-driven insights",
            "duration_seconds": 10
          }
        ]

        DESIGN PRINCIPLES:
        - Image and text must be designed together as one coordinated system
        - Light, professional color schemes (avoid dark or bright colors)
        - Clear visual hierarchy with designated text areas
        - Educational infographic style, not decorative backgrounds
        - Text should be substantial and informative, not just keywords

        IMPORTANT: Return ONLY the JSON array, nothing else. No ```json``` markers, no explanations.
        """

        user_prompt = {
            "task": "analyze_text_for_video_segments",
            "text_content": text_content,
            "segments_count": segments_count,
            "target_duration": target_duration,
            "requirements": [
                "Create logical, flowing segments",
                "Each segment covers one main concept",
                "Suitable for 8-12 seconds of narration",
                "Include detailed image generation prompts",
                "Professional, educational tone"
            ]
        }

        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_prompt
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

                segments = json.loads(fixed_result)
                print(f"✅ Fixed JSON and created {len(segments)} segments")
                return segments
            except json.JSONDecodeError as e2:
                print(f"❌ Could not fix JSON: {e2}")
                print(f"Final attempt - showing problematic area:")
                print(result[max(0, len(result)//2-100):len(result)//2+100])
                return None
    
    def enhance_single_prompt(self, original_prompt):
        """
        Enhance image prompts to create coordinated infographic layouts with specific empty placeholders

        Args:
            original_prompt: Basic image prompt from Gemini

        Returns:
            Enhanced prompt for light-colored infographic with empty text areas
        """
        if not original_prompt:
            return original_prompt

        enhancement_template = f"""
        Create a light-colored, professional infographic layout for an explainer video.

        BASE DESIGN CONCEPT:
        {original_prompt}

        CRITICAL REQUIREMENTS:
        - Light color palette: whites, light blues, soft pastels, light grays
        - 16:9 aspect ratio (1920x1080 pixels)
        - Professional infographic/educational style
        - Clean, minimal, uncluttered design

        EMPTY PLACEHOLDER AREAS (ESSENTIAL):
        - Create specific empty rectangular or box areas for text placement
        - These areas should have light backgrounds (white, very light blue, etc.)
        - Position placeholders logically based on the content flow
        - Ensure placeholders are clearly defined and spacious
        - NO TEXT OR TYPOGRAPHY in the image - only empty spaces for text

        VISUAL ELEMENTS:
        - Simple, clean icons and illustrations related to the topic
        - Connecting arrows, lines, or flow indicators where appropriate
        - Visual hierarchy that guides the eye through the content
        - Subtle visual elements that support but don't compete with text
        - Professional business/educational aesthetic

        LAYOUT STRUCTURE:
        - Organize content in a logical flow (top to bottom, left to right)
        - Create clear sections or areas for different types of information
        - Use plenty of white space and breathing room
        - Ensure the design supports structured text content (lists, steps, explanations)

        COLOR AND STYLE:
        - Predominantly light colors (white backgrounds, light blue accents)
        - Soft, professional color scheme suitable for business presentations
        - Avoid dark, bright, or distracting colors
        - Clean, modern infographic style
        - Suitable for overlaying detailed text content

        The image should function as a structured template ready for detailed text overlays.
        """

        return enhancement_template.strip()

    def generate_enhanced_prompts(self, segments):
        """
        Enhance image prompts for better generation quality

        Args:
            segments: List of video segments with basic image prompts

        Returns:
            Enhanced segments with improved image prompts
        """
        print("🎨 Enhancing image prompts for better generation...")

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

        total_duration = sum(seg.get('duration_seconds', 10) for seg in enhanced_segments)

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
                "duration_seconds": segment.get('duration_seconds', 10),
                "background_image": image_path,
                "timing": {
                    "start_time": sum(seg.get('duration_seconds', 10) for seg in enhanced_segments[:i-1]),
                    "end_time": sum(seg.get('duration_seconds', 10) for seg in enhanced_segments[:i])
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
