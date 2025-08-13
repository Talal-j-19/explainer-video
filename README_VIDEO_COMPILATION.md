# 🎬 Video Compiler for Explainer Videos

This module compiles your explainer video assets into a complete video by combining background images with audio segments, then concatenating all segments into a final video file.

## 🎯 What It Does

1. **Compiles Individual Segments** - Combines each background image with its corresponding audio
2. **Synchronizes Audio & Video** - Matches image duration to audio length
3. **Concatenates Segments** - Joins all segments into one complete video
4. **Professional Output** - Creates high-quality MP4 videos ready for sharing

## 🚀 Quick Start

### 1. Prerequisites

**FFmpeg Required**: The video compiler uses FFmpeg for video processing.

```bash
# Windows: Download from https://ffmpeg.org/download.html
# Or use chocolatey: choco install ffmpeg

# macOS: brew install ffmpeg

# Linux: sudo apt install ffmpeg
```

### 2. Generate Video Assets First

Before compiling, you need the complete pipeline assets:

```bash
# Generate everything including audio
python create_explainer_video.py

# Or use Edge TTS for better quality
python create_explainer_video.py --tts-service edge_tts
```

### 3. Compile the Video

```bash
# Compile complete video (default: 1080p, 30fps)
python video_compiler.py

# Compile only segments (for testing)
python video_compiler.py --segments-only

# Custom resolution and frame rate
python video_compiler.py --resolution 720p --fps 24
```

## 🔧 Command Line Options

```bash
python video_compiler.py [OPTIONS]

Options:
  --output-dir DIR        Output directory (default: generated_videos)
  --resolution RES        Video resolution: 720p, 1080p, 4k (default: 1080p)
  --fps RATE             Frame rate (default: 30)
  --segments-only        Only compile segments, don't concatenate
  -h, --help            Show help message
```

## 📁 Output Structure

```
generated_videos/
├── segment_01_video.mp4      # Individual segment videos
├── segment_02_video.mp4
├── segment_03_video.mp4
├── ...
├── explainer_video_1234567890.mp4  # Final complete video
└── video_compilation_summary.md     # Compilation report
```

## 🎬 Video Quality Settings

### Resolutions Available
- **720p**: 1280x720 (good for web, smaller file size)
- **1080p**: 1920x1080 (HD, recommended for most uses)
- **4K**: 3840x2160 (ultra-high quality, large file size)

### Frame Rates
- **24 fps**: Film-like, cinematic feel
- **30 fps**: Standard video, smooth motion
- **60 fps**: High frame rate, very smooth (larger files)

### Codecs
- **Video**: H.264 (libx264) - Widely compatible
- **Audio**: AAC - High quality, small file size

## 🔄 Complete Workflow

### Step 1: Generate Assets
```bash
python create_explainer_video.py
# Creates: text, images, audio, scripts
```

### Step 2: Compile Video
```bash
python video_compiler.py
# Creates: individual segments + final video
```

### Step 3: Review & Share
- Check video quality
- Verify audio synchronization
- Share your explainer video!

## 🧪 Testing

Test the video compiler setup:

```bash
# Check if everything is ready
python test_video_compiler.py

# Test segment compilation only
python video_compiler.py --segments-only

# Test complete compilation
python video_compiler.py
```

## 📊 Expected Results

### Successful Compilation
```
🎬 COMPILING ALL VIDEO SEGMENTS
==================================================
📋 Found 3 segments to compile

🎬 Compiling Segment 1...
   ⏱️  Audio duration: 8.45 seconds
   🎯 Output: segment_01_video.mp4
   ✅ Segment 1 compiled successfully (2048576 bytes)

🎬 Compiling Segment 2...
   ⏱️  Audio duration: 7.23 seconds
   🎯 Output: segment_02_video.mp4
   ✅ Segment 2 compiled successfully (1876544 bytes)

🎬 Compiling Segment 3...
   ⏱️  Audio duration: 9.12 seconds
   🎯 Output: segment_03_video.mp4
   ✅ Segment 3 compiled successfully (2345678 bytes)

📊 Segment compilation summary:
   Total segments: 3
   Successful: 3
   Failed: 0

🎬 CONCATENATING 3 VIDEO SEGMENTS
==================================================
🎯 Final output: explainer_video_1234567890.mp4
📋 Created video list file: video_list.txt
🔧 Running FFmpeg concatenation...
✅ Video concatenation successful!
   📁 Output file: explainer_video_1234567890.mp4
   📊 File size: 6270800 bytes

🎉 COMPLETE VIDEO COMPILED SUCCESSFULLY!
📁 Final video: generated_videos/explainer_video_1234567890.mp4
📊 Total segments: 3
```

## 🚨 Troubleshooting

### Common Issues

**"FFmpeg not found"**
```bash
# Install FFmpeg first
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

**"Video script not found"**
```bash
# Run the explainer video generator first
python create_explainer_video.py
```

**"Audio files not found"**
```bash
# Generate audio with TTS first
python create_explainer_video.py --tts-service gtts
```

**"Background images not found"**
```bash
# Generate images first
python create_explainer_video.py
```

### Performance Issues

**Slow compilation**
- Use lower resolution: `--resolution 720p`
- Lower frame rate: `--fps 24`
- Check available disk space

**Large file sizes**
- Use 720p instead of 1080p
- Lower frame rate
- Consider video compression tools

## 🔧 Advanced Usage

### Programmatic Usage

```python
from video_compiler import VideoCompiler

# Initialize compiler
compiler = VideoCompiler()

# Custom settings
compiler.video_width = 1280
compiler.video_height = 720
compiler.fps = 24

# Compile complete video
final_video = compiler.compile_complete_video()

if final_video:
    print(f"Video compiled: {final_video}")
else:
    print("Compilation failed")
```

### Custom Video Settings

```python
# High quality settings
compiler.video_width = 1920
compiler.video_height = 1080
compiler.fps = 60
compiler.video_codec = "libx264"
compiler.audio_codec = "aac"

# Custom bitrates
# Modify the compile_segment method for custom bitrates
```

## 📈 Quality vs. Performance

### Fast Compilation (Lower Quality)
```bash
python video_compiler.py --resolution 720p --fps 24
# Smaller files, faster processing
```

### Balanced Quality (Recommended)
```bash
python video_compiler.py --resolution 1080p --fps 30
# Good quality, reasonable file size
```

### High Quality (Slower)
```bash
python video_compiler.py --resolution 4k --fps 60
# Best quality, larger files, slower processing
```

## 🎬 Video Production Tips

### Before Compilation
1. **Review audio quality** - Listen to generated audio files
2. **Check image quality** - Ensure background images are clear
3. **Verify timing** - Audio should match intended segment length

### After Compilation
1. **Check synchronization** - Audio should match video timing
2. **Review quality** - Ensure video meets your standards
3. **Test playback** - Verify compatibility with different players

### Optimization
1. **Use appropriate resolution** - Higher isn't always better
2. **Choose frame rate wisely** - 30fps is usually sufficient
3. **Consider file size** - Balance quality with sharing needs

## 🔮 Future Enhancements

- **Text overlay integration** - Add text overlays to video
- **Transition effects** - Smooth transitions between segments
- **Custom animations** - Animated elements in video
- **Multiple output formats** - MP4, WebM, MOV support
- **Batch processing** - Compile multiple projects

## 🎉 Success!

Once compilation is complete, you'll have:

- ✅ **Individual segment videos** for editing
- ✅ **Complete explainer video** ready for sharing
- ✅ **Professional quality** MP4 output
- ✅ **Perfect synchronization** between audio and video
- ✅ **Multiple resolution options** for different use cases

Your explainer video is now ready for:
- **Social media sharing**
- **Website embedding**
- **Presentation use**
- **Further editing** in video software
- **Professional distribution**

## 📝 Example Workflow

```bash
# 1. Generate complete assets
python create_explainer_video.py --tts-service edge_tts

# 2. Test video compiler
python test_video_compiler.py

# 3. Compile segments only (test)
python video_compiler.py --segments-only

# 4. Compile complete video
python video_compiler.py --resolution 1080p --fps 30

# 5. Check results
ls -la generated_videos/
```

**Start creating professional explainer videos today!** 🎬✨
