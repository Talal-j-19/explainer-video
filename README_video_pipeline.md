# Explainer Video Generation Pipeline

## 🎬 Overview

This system creates complete explainer video assets from text content using AI-powered analysis, structured JSON prompting, and multiple image generation services.

## 🔄 New Improved Pipeline

### **Two-Step Process:**
1. **Gemini analyzes text** → Generates detailed image prompts
2. **Image generators use prompts** → Create professional backgrounds

### **Key Improvements:**
- ✅ **Separated concerns**: Text analysis vs image generation
- ✅ **JSON prompting**: Structured, reliable communication with AI
- ✅ **System prompts**: More accurate and consistent results
- ✅ **Multiple image services**: Gemini, Stability AI, DALL-E, fallbacks
- ✅ **Enhanced prompts**: Two-stage prompt refinement for better images

## 📁 File Structure

```
video_explainer_generator.py    # Core text analysis & script generation
image_generator.py              # Multi-service image generation
create_explainer_video.py       # Complete pipeline orchestrator
test_video_pipeline.py          # Testing and validation
```

## 🚀 Usage

### Quick Start
```bash
python create_explainer_video.py
```

### Individual Components
```bash
# Generate script only
python video_explainer_generator.py

# Generate images from existing script
python image_generator.py video_segments/video_script.json

# Test the pipeline
python test_video_pipeline.py
```

## 🔧 How It Works

### 1. Text Analysis (JSON Prompting)
```python
# Input: User text content
# Output: Structured JSON with segments

{
  "segment_number": 1,
  "title": "AI Business Impact",
  "narration_text": "AI is transforming businesses with 25% productivity gains...",
  "text_overlay": "25% Productivity Increase",
  "key_points": ["productivity", "cost reduction", "automation"],
  "image_prompt": "Professional business chart showing upward growth trends...",
  "duration_seconds": 10
}
```

### 2. Prompt Enhancement
```python
# Gemini enhances basic prompts for better image generation
# Input: Basic image prompt
# Output: Detailed, optimized prompt for AI image models

"Professional business chart showing upward growth trends, 
modern minimalist style, 16:9 aspect ratio, clean composition 
with space for text overlays, corporate blue and white color scheme,
high contrast for readability, suitable for explainer video background"
```

### 3. Multi-Service Image Generation
```python
# Priority order:
1. Gemini Image Generation (preferred)
2. Stability AI (high quality)
3. OpenAI DALL-E (creative)
4. Simple backgrounds (fallback)
```

## 🎯 Output Structure

### Generated Assets
```
video_segments/
├── video_script.json              # Complete video plan
├── segment_01_background.png       # Background images
├── segment_02_background.png
├── segment_01_narration.txt        # TTS scripts
├── segment_01_overlay.txt          # Text overlays
├── complete_narration.txt          # Full narration
└── production_summary.md           # Production guide
```

### Script JSON Structure
```json
{
  "video_metadata": {
    "total_segments": 5,
    "estimated_duration": 60,
    "generation_method": "gemini_with_separate_prompts"
  },
  "segments": [
    {
      "segment_number": 1,
      "title": "Introduction",
      "narration_text": "Welcome to our explanation of...",
      "text_overlay": "Key Concept",
      "image_prompt": "Detailed prompt for image generation...",
      "background_image": "segment_01_background.png",
      "timing": {"start_time": 0, "end_time": 12}
    }
  ]
}
```

## 🔑 Configuration

### Required API Keys (.env file)
```bash
GOOGLE_API_KEY=your_gemini_api_key          # Required for text analysis
STABILITY_API_KEY=your_stability_key        # Optional (better images)
OPENAI_API_KEY=your_openai_key             # Optional (DALL-E images)
```

### System Prompts
The pipeline uses carefully crafted system prompts for:
- **Text Analysis**: Structured video segment extraction
- **Prompt Enhancement**: Optimizing image generation prompts
- **JSON Validation**: Ensuring consistent output format

## 🎨 Image Generation Methods

### 1. Gemini Image Generation
```python
def generate_with_gemini(self, prompt, output_path):
    # Enhanced prompt with professional requirements
    enhanced_prompt = f"""
    Create a professional background image for an explainer video.
    Requirements: 16:9 aspect ratio, clean composition, 
    suitable for text overlays...
    Content: {prompt}
    """
    # Generate using Gemini's image model
```

### 2. Fallback Methods
- **Stability AI**: High-quality Stable Diffusion
- **OpenAI DALL-E**: Creative and accurate
- **Simple Backgrounds**: Gradient backgrounds with PIL

## 📊 Quality Improvements

### JSON Prompting Benefits
- **Structured Output**: Consistent, parseable responses
- **Error Reduction**: Less parsing failures
- **Rich Metadata**: Detailed segment information
- **Validation**: Easy to verify completeness

### System Prompts Benefits
- **Role Clarity**: AI understands its specific role
- **Consistent Style**: Uniform output format
- **Better Results**: More accurate content generation
- **Specialized Tasks**: Optimized for each pipeline step

## 🧪 Testing

### Run Tests
```bash
python test_video_pipeline.py
```

### Test Components
1. **JSON Prompting Test**: Validates structured communication
2. **Complete Pipeline Test**: End-to-end functionality
3. **Image Generation Test**: Multiple service fallbacks

## 🎬 Production Workflow

### 1. Generate Assets
```bash
python create_explainer_video.py
# Input your text content
# Get complete video assets
```

### 2. Create Audio (TTS)
```bash
# Use your preferred TTS service
gtts-cli -f segment_01_narration.txt -o segment_01_audio.mp3
```

### 3. Assemble Video
```bash
# Use FFmpeg or video editing software
# Combine backgrounds + text overlays + audio
```

## 🔮 Future Enhancements

- **Real Gemini Image API**: When available, replace placeholder
- **Video Assembly**: Automated FFmpeg integration
- **Advanced Animations**: Text overlay animations
- **Voice Cloning**: Custom narrator voices
- **Multi-language**: International video generation

## 🎉 Benefits Summary

✅ **Separated Concerns**: Better maintainability and flexibility
✅ **JSON Structure**: Reliable, parseable communication
✅ **System Prompts**: More accurate AI responses
✅ **Multiple Services**: Robust fallback options
✅ **Enhanced Quality**: Two-stage prompt optimization
✅ **Production Ready**: Complete asset generation pipeline

This improved pipeline provides a robust, scalable solution for creating professional explainer videos from any text content!
