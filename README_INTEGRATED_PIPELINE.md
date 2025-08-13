# Integrated Explainer Video Pipeline with TTS

This is the complete explainer video creation pipeline that combines text analysis, image generation, and **automatic TTS audio generation** into a single workflow.

## 🎯 What's New

The pipeline now includes **automatic TTS (Text-to-Speech)** generation, so you can create complete video assets including audio narration from a single command!

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
pip install -r requirements_tts.txt

# Or install individually
pip install gtts edge-tts
```

### 2. Run the Complete Pipeline

```bash
# Generate everything including audio (default)
python create_explainer_video.py

# Use Edge TTS for better quality
python create_explainer_video.py --tts-service edge_tts

# Skip TTS if you only want text/image assets
python create_explainer_video.py --no-tts
```

## 🎵 TTS Options

### Available Services

- **`gtts`** (default) - Google TTS, free, good quality
- **`edge_tts`** - Microsoft Edge TTS, free, very good quality
- **`azure`** - Azure Cognitive Services, paid, excellent quality
- **`simple`** - Basic beep sounds for testing

### Command Line Examples

```bash
# Google TTS with Spanish
python create_explainer_video.py --tts-service gtts --lang es

# Edge TTS with British voice
python create_explainer_video.py --tts-service edge_tts --voice en-GB-RyanNeural

# Azure TTS (requires API keys)
python create_explainer_video.py --tts-service azure --voice en-US-AriaNeural

# No TTS - just text and images
python create_explainer_video.py --no-tts
```

## 🔄 Complete Workflow

The integrated pipeline now performs these steps automatically:

1. **📝 Text Analysis** - Converts input text to video script
2. **🎨 Image Generation** - Creates background images for each segment
3. **📝 Text Overlays** - Generates overlay text files
4. **🗣️ Narration Scripts** - Creates narration text files
5. **🎵 Audio Generation** - **NEW!** Automatically converts narration to audio using TTS
6. **📋 Production Summary** - Creates comprehensive guide for video production

## 📁 Output Structure

```
video_segments/
├── video_script.json              # Complete video metadata
├── segment_01_background.png      # Background images
├── segment_01_overlay.txt         # Text overlays
├── segment_01_narration.txt       # Narration scripts
├── segment_02_background.png
├── segment_02_overlay.txt
├── segment_02_narration.txt
├── ... (more segments)
├── complete_narration.txt         # Full narration script
├── audio/                         # 🎵 NEW! Generated audio files
│   ├── segment_01_audio.mp3      # Individual segment audio
│   ├── segment_02_audio.mp3
│   ├── ...
│   ├── complete_narration_audio.mp3  # All segments combined
│   └── audio_generation_summary.md   # Audio generation report
└── production_summary.md          # Complete production guide
```

## 🎬 Video Production Ready

With the integrated pipeline, you now have:

✅ **Complete video script** with timing and metadata  
✅ **Background images** for each segment  
✅ **Text overlays** ready for video editing  
✅ **Audio narration** automatically generated from TTS  
✅ **Production guide** with next steps  

## 🧪 Testing

Test the integrated functionality:

```bash
# Test the complete pipeline
python test_integrated_pipeline.py

# Test TTS functionality separately
python test_tts.py
```

## 🔧 Advanced Usage

### Programmatic Usage

```python
from create_explainer_video import ExplainerVideoCreator

creator = ExplainerVideoCreator()

# Generate complete assets with TTS
result = creator.create_complete_video_assets(
    text_content="Your text here",
    target_duration=60,
    segments_count=5,
    enable_tts=True,
    tts_service='edge_tts',
    tts_kwargs={'voice': 'en-US-AriaNeural'}
)

# Check generated audio files
print(f"Generated {len(result['audio_files'])} audio files")
```

### Custom TTS Configuration

```python
# Edge TTS with custom voice
tts_kwargs = {
    'voice': 'en-GB-RyanNeural',
    'rate': '+0%',  # Speed adjustment
    'volume': '+0%'  # Volume adjustment
}

result = creator.create_complete_video_assets(
    text_content="Your text",
    enable_tts=True,
    tts_service='edge_tts',
    tts_kwargs=tts_kwargs
)
```

## 🎵 TTS Service Comparison

| Service | Quality | Cost | Setup | Best For |
|---------|---------|------|-------|-----------|
| **gTTS** | Good | Free | None | Beginners, quick demos |
| **Edge TTS** | Very Good | Free | None | Production quality, free |
| **Azure** | Excellent | Pay-per-use | API keys | Enterprise, customization |
| **Simple** | Basic | Free | None | Testing, development |

## 🚨 Troubleshooting

### TTS Issues

**"gTTS: Package not installed"**
```bash
pip install gtts
```

**"Edge TTS: Package not installed"**
```bash
pip install edge-tts
```

**Audio files not generated**
- Check narration files exist
- Verify TTS service is working
- Check disk space and permissions

### Pipeline Issues

**Import errors**
```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
pip install -r requirements_tts.txt
```

**Image generation fails**
- Check API keys for image services
- Verify internet connection

## 📈 Performance Tips

1. **Use Edge TTS** for best quality/speed balance
2. **Skip TTS** (`--no-tts`) for quick text/image generation
3. **Batch process** multiple projects
4. **Test with simple TTS** first, then upgrade to better quality

## 🎉 Success!

Once the pipeline completes, you'll have:

- ✅ **Professional video script** with perfect timing
- ✅ **High-quality background images** for each segment  
- ✅ **Ready-to-use text overlays**
- ✅ **Professional audio narration** automatically generated
- ✅ **Complete production guide** for final video creation

Your explainer video is now ready for final assembly in any video editing software!

## 🔮 Future Enhancements

- **Voice cloning** - Custom voice training
- **Emotion control** - Happy, sad, excited tones
- **Speed adjustment** - Faster/slower narration
- **Batch processing** - Multiple video projects
- **Video export** - Direct MP4 generation
