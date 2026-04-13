# Explainer Video Generation System

A comprehensive system for generating explainer videos with integrated text-to-speech, image generation, and video compilation capabilities.

## Features

- **Text-to-Speech**: Google TTS (gTTS) integration with high-quality audio generation
- **Image Generation**: Template-based infographic system with consistent styling
- **Video Compilation**: Automated video assembly from audio and visual segments
- **API Integration**: FastAPI server for web-based video generation
- **Modular Design**: Separate processors for TTS, images, and video compilation

## Setup Guide

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd explainer-video
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Environment Configuration

1. **Create `.env` file** in the project root:
   ```bash
   GEMINI_API_KEY=your_google_gemini_api_key_here
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

2. **Get API Keys:**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Add the key to your `.env` file

## Usage

### Command Line Usage

Generate a complete explainer video:

```bash
python create_explainer_video_integrated.py "Your Topic Here" --duration 60 --output-dir output_videos
```

**Parameters:**
- `"Your Topic Here"`: Topic for the explainer video (required)
- `--duration 60`: Target video duration in seconds (default: 60)
- `--output-dir output_videos`: Output directory (default: generated_videos)

### API Server Usage

Start the FastAPI server:

```bash
python main.py
```

The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### API Endpoints

#### `POST /generate`

Generate a new explainer video from text.

**Request Body (JSON):**
```json
{
  "text_content": "Artificial Intelligence is transforming modern technology...",
  "target_duration": 60,
  "segments_count": null,
  "enable_tts": true,
  "tts_service": "gemini_tts",
  "lang": "en",
  "color_scheme": "modern_blue"
}
```

**Response (JSON):**
```json
{
  "status": "success",
  "job_id": "1727693820",
  "download_url": "/videos/job_1727693820/final_video.mp4"
}
```

#### `GET /videos/{job_id}/final_video.mp4`

Download the generated video file.

## TTS Service

### Overview

The system includes a newly integrated Text-to-Speech service using Google's TTS technology:

- **Service Name**: `gemini_tts`
- **Technology**: Google Text-to-Speech (gTTS)
- **Audio Format**: WAV files for video compatibility
- **Quality**: High-quality, natural-sounding speech
- **Languages**: English (configurable)

### TTS Services Available

| Service | Status | Description |
|----------|--------|-------------|
| `gemini_tts` | Active | Google TTS (gTTS) - Primary service |
| `custom_api` | Deprecated | Legacy custom API - Not recommended |

### TTS Configuration

The TTS service automatically handles:
- Text cleaning and preprocessing
- Audio file generation in WAV format
- Temporary file management and cleanup
- Thread-safe processing for parallel operations
- Error handling and retry logic

## Image Generation

### Template-Based System

The integrated image generator uses template-based infographics with:

- **Consistent Color Schemes**: Professional color palettes
- **Layout Variety**: Multiple infographic styles
- **Text Overlay**: Dynamic text placement
- **High Resolution**: Optimized for video output
- **Parallel Processing**: Efficient batch generation

### Color Schemes

- `modern_blue`: Professional blue gradient
- `tech_green`: Technology-focused green theme
- `corporate_gray`: Business-oriented gray palette
- `vibrant_purple`: Creative purple gradient

## Project Structure

```bash
explainer-video/
|-- main.py                          # FastAPI server
|-- create_explainer_video_integrated.py  # Main video generation
|-- tts_processor.py                  # TTS service
|-- integrated_image_generator.py       # Image generation
|-- video_compiler.py               # Video assembly
|-- video_explainer_generator.py       # Script generation
|-- requirements.txt                  # Dependencies
|-- .env                            # Environment variables
|-- video_segments/                 # Generated content
`-- generated_videos/                # Final videos
```

## Testing

### TTS Service Test

Test the TTS service independently:

```bash
python -c "
from tts_processor import TTSProcessor
tts = TTSProcessor('test_output')
result = tts.generate_audio_for_segment({
    'segment_number': 1,
    'clean_text': 'Hello, this is a test of the TTS service.',
    'output_audio': 'test_output/test.wav'
}, tts_service='gemini_tts')
print('TTS Test Result:', result)
"
```

### Integration Test

Test the complete pipeline:

```bash
python test_integration.py
```

## Troubleshooting

### Common Issues

#### "Unknown TTS service: custom_api"
**Cause**: Code still using deprecated service name
**Solution**: Ensure all calls use `tts_service='gemini_tts'`

#### "API key expired"
**Cause**: Google API key has expired
**Solution**: 
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate new API key
3. Update `.env` file with new key

#### "Audio generation had issues"
**Cause**: TTS service failing to generate audio
**Solution**:
1. Check internet connection
2. Verify API key is valid
3. Check available disk space
4. Review TTS service logs

#### "ModuleNotFoundError: No module named 'gtts'"
**Cause**: Missing TTS dependencies
**Solution**:
```bash
pip install gtts pydub
```

#### "File locking errors"
**Cause**: Multiple processes accessing same audio files
**Solution**: Ensure single process execution or use file locking

### Debug Mode

Enable verbose logging:

```bash
export PYTHONPATH=$PYTHONPATH:.
python create_explainer_video_integrated.py "Topic" --duration 30 2>&1 | tee debug.log
```

## Performance

### Benchmarks

- **TTS Generation**: ~2-4 seconds per segment
- **Image Generation**: ~5-15 seconds per segment
- **Complete Video**: ~2-5 minutes for 60-second video
- **Parallel Processing**: Up to 10 concurrent segments

### Optimization Tips

1. **Use SSD storage** for faster file I/O
2. **Increase memory** for larger videos
3. **Stable internet** for API calls
4. **Close unused applications** to free resources

## Security

### API Keys

- Never commit API keys to version control
- Use environment variables for all secrets
- Rotate API keys regularly
- Monitor API usage and costs

### File Permissions

- Ensure write permissions for output directories
- Check antivirus software isn't blocking file operations
- Validate temporary file access

## Contributing

### Development Setup

1. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```

2. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

3. **Code formatting:**
   ```bash
   black .
   flake8 .
   ```

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request with description

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:

1. **Check the troubleshooting section** above
2. **Search existing issues** in the repository
3. **Create new issue** with:
   - Detailed error description
   - System information
   - Steps to reproduce
   - Expected vs actual behavior

---

**Last Updated**: October 2024  
**Version**: 2.0.0  
**Compatibility**: Python 3.8+, Windows/Linux/macOS
