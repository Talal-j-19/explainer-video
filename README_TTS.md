# TTS Processor for Explainer Video Narrations

This module provides text-to-speech functionality to convert narration text files into audio files for your explainer videos.

## 🎯 What It Does

1. **Cleans narration text** - Removes metadata headers and extracts clean text for TTS
2. **Generates audio files** - Creates MP3 files for each video segment
3. **Multiple TTS services** - Supports Google TTS, Edge TTS, Azure, and fallback options
4. **Complete audio** - Generates a combined audio file with all segments
5. **Comprehensive summary** - Creates detailed reports of the audio generation process

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install TTS packages
pip install -r requirements_tts.txt

# Or install individually
pip install gtts edge-tts
```

### 2. Basic Usage

```bash
# Generate audio using Google TTS (default)
python tts_processor.py

# Use Edge TTS instead
python tts_processor.py --service edge_tts

# Only clean text without generating audio
python tts_processor.py --clean-only
```

### 3. Check Results

Generated audio files will be saved in `video_segments/audio/`:
- `segment_01_audio.mp3` - Audio for segment 1
- `segment_02_audio.mp3` - Audio for segment 2
- `complete_narration_audio.mp3` - All segments combined
- `audio_generation_summary.md` - Detailed report

## 🎵 TTS Services

### Google TTS (gTTS) - **Recommended for beginners**
- **Cost**: Free
- **Quality**: Good
- **Languages**: 100+ languages
- **Setup**: No API keys needed

```bash
python tts_processor.py --service gtts --lang en
```

### Microsoft Edge TTS - **Recommended for quality**
- **Cost**: Free
- **Quality**: Very good
- **Voices**: Natural-sounding neural voices
- **Setup**: No API keys needed

```bash
python tts_processor.py --service edge_tts --voice en-US-AriaNeural
```

### Azure Cognitive Services - **Enterprise quality**
- **Cost**: Pay-per-use
- **Quality**: Excellent
- **Features**: Advanced voice customization
- **Setup**: Requires Azure account and API keys

```bash
# Set environment variables first
export AZURE_SPEECH_KEY="your_key_here"
export AZURE_SPEECH_REGION="eastus"

python tts_processor.py --service azure --voice en-US-AriaNeural
```

### Simple Audio Fallback - **For testing**
- **Cost**: Free
- **Quality**: Basic beep sounds
- **Use case**: Testing workflow without external services

```bash
python tts_processor.py --service simple
```

## 📁 File Structure

```
video_segments/
├── segment_01_narration.txt     # Original narration with metadata
├── segment_02_narration.txt
├── segment_03_narration.txt
├── complete_narration.txt
├── audio/                        # Generated audio files
│   ├── segment_01_audio.mp3
│   ├── segment_02_audio.mp3
│   ├── segment_03_audio.mp3
│   ├── complete_narration_audio.mp3
│   └── audio_generation_summary.md
└── video_script.json            # Video metadata
```

## 🔧 Advanced Usage

### Custom Voices (Edge TTS)

```bash
# List available voices
python -c "import edge_tts; print(edge_tts.list_voices())"

# Use specific voice
python tts_processor.py --service edge_tts --voice en-GB-RyanNeural
```

### Language Options (gTTS)

```bash
# Spanish
python tts_processor.py --service gtts --lang es

# French
python tts_processor.py --service gtts --lang fr

# German
python tts_processor.py --service gtts --lang de
```

### Programmatic Usage

```python
from tts_processor import TTSProcessor

# Initialize processor
processor = TTSProcessor()

# Clean narrations
cleaned = processor.clean_all_narrations()

# Generate audio with specific service
narrations = processor.generate_all_audio('edge_tts', voice='en-US-AriaNeural')

# Create summary
processor.create_audio_summary(narrations)
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_tts.py
```

This will:
1. Test text cleaning functionality
2. Test audio generation with simple fallback
3. Show sample cleaned text
4. Provide next steps

## 📊 Output Files

### Audio Files
- **Format**: MP3
- **Quality**: Depends on TTS service
- **Naming**: `segment_XX_audio.mp3` where XX is segment number

### Summary Report
- **File**: `audio_generation_summary.md`
- **Content**: 
  - Generation timestamp
  - Segment details
  - Audio file information
  - TTS service used
  - File sizes
  - Next steps for video production

## 🎬 Next Steps for Video Production

1. **Review audio quality** - Listen to generated files
2. **Import into video editor** - Use with DaVinci Resolve, Premiere, etc.
3. **Sync with visuals** - Match audio timing with background images
4. **Add text overlays** - Use the overlay text files
5. **Export final video** - Combine all elements

## 🚨 Troubleshooting

### Common Issues

**"gTTS: Package not installed"**
```bash
pip install gtts
```

**"Edge TTS: Package not installed"**
```bash
pip install edge-tts
```

**"Azure: Missing environment variables"**
```bash
export AZURE_SPEECH_KEY="your_key"
export AZURE_SPEECH_REGION="eastus"
```

**Audio files not generated**
- Check narration files exist in `video_segments/`
- Verify TTS service is working
- Check disk space and permissions

### Quality Issues

**Robotic voice (gTTS)**
- Try Edge TTS instead: `--service edge_tts`
- Adjust language settings: `--lang en`

**Slow generation**
- Use `--service simple` for testing
- Check internet connection for online services

## 🔮 Future Enhancements

- **Voice cloning** - Custom voice training
- **Emotion control** - Happy, sad, excited tones
- **Speed adjustment** - Faster/slower narration
- **Batch processing** - Multiple video projects
- **Audio post-processing** - Noise reduction, normalization

## 📝 Example Workflow

```bash
# 1. Clean and generate audio for all segments
python tts_processor.py --service edge_tts

# 2. Check results
ls -la video_segments/audio/

# 3. Listen to sample
# (Use your audio player to preview files)

# 4. Create video with generated audio
# (Import into your video editing software)
```

## 🎉 Success!

Once audio generation is complete, you'll have:
- ✅ Clean narration text (metadata removed)
- ✅ Individual segment audio files
- ✅ Complete narration audio file
- ✅ Detailed generation summary
- ✅ Ready-to-use audio for video production

Your explainer video workflow is now complete with professional-quality audio narration!
