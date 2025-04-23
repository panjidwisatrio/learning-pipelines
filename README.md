# LinkedIn Learning Pipeline

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)

A comprehensive pipeline for processing LinkedIn Learning videos, generating subtitles, summarizing content, and creating structured documents.

## Background

The LinkedIn Learning Pipeline is a tool designed to enhance the learning experience with LinkedIn Learning courses. It automates the process of converting videos to text content through transcription, summarization, and document generation. This tool helps users:

- Transcribe LinkedIn Learning videos to SRT subtitle format
- Convert subtitles to plain text 
- Generate AI-powered summaries and key points from video content
- Create well-formatted Markdown and DOCX documents from the processed content

This pipeline streamlines the process of creating structured documentation and study materials from video courses, making it easier to review and reference course content.

## Installation

### Prerequisites

- Python 3.6 or higher
- Pandoc 3.6.4 (included in the repository)
- FFmpeg (for video processing)
- GPU support (optional, for faster transcription)
- PyTorch with CUDA (optional, for GPU acceleration)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/linkedin-learning-pipeline.git
   cd linkedin-learning-pipeline
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Pandoc (if not using the included version):
   - Windows: Run the included installer at `pandoc-3.6.4-windows-x86_64.msi`
   - macOS: `brew install pandoc`
   - Linux: `apt-get install pandoc`

5. Install FFmpeg:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg`

6. Setup Local AI with LM Studio (optional):
   - Download and install [LM Studio](https://lmstudio.ai/) for your operating system
   - Launch LM Studio and download the `qwen2.5-7b-instruct-1m` model:
     - Go to the Models tab
     - Search for "qwen2.5-7b-instruct-1m"
     - Download the model (approximately 4GB)
   - Start the local server:
     - Select the downloaded model
     - Click "Start Server" in the bottom-left corner
     - The server should run on `http://localhost:1234/v1`
   - Update `config.yaml` if needed:
     ```yaml
     openai:
       model: "qwen2.5-7b-instruct-1m"
       api_key: "lm-studio"  # This can be any value when using LM Studio locally
       base_url: "http://localhost:1234/v1"
       max_tokens: 4000
       timeout: 60
     ```

## Usage

### Basic Usage

The pipeline can be run with the following command:

```bash
python main.py -i <input_path> -o <output_directory> -s <steps>
```

Where:
- `-i, --input`: Path to input file or directory containing videos or subtitle files
- `-o, --output`: Optional output directory for processed files
- `-s, --steps`: Processing steps to perform (default: all)
  - Available steps: `srt2txt`, `txt2md`, `md2docx`, `all`

### Examples

1. Process a single video file through the entire pipeline:
   ```bash
   python main.py -i path/to/video.mp4
   ```

2. Process all SRT files in a directory to TXT format:
   ```bash
   python main.py -i path/to/subtitles/ -s srt2txt
   ```

3. Convert TXT files to Markdown with summaries:
   ```bash
   python main.py -i path/to/text_files/ -s txt2md
   ```

4. Convert Markdown files to DOCX format:
   ```bash
   python main.py -i path/to/markdown_files/ -s md2docx -o path/to/output/
   ```

### Transcribing Videos

To generate SRT subtitles directly from video files:

```bash
python -c "from app.generate_srt import transcribe_to_srt; transcribe_to_srt('path/to/video.mp4')"
```

The script will use Whisper to transcribe the video and save an SRT file with the same name as the video file. Note that if an SRT file with the same name already exists, the transcription will be skipped to avoid redundant processing.

## Application Flow

The pipeline follows these steps:

1. **Video Transcription**: Converts video to SRT subtitle format using OpenAI's Whisper model
   > **Note**: Transcription is only performed if the video doesn't already have a corresponding .srt file
2. **SRT to TXT Conversion**: Extracts plain text from SRT files, removing timestamps
3. **TXT to MD Transformation**: Processes text files to create structured Markdown documents with summaries and key points
4. **MD to DOCX Conversion**: Converts Markdown to DOCX format with proper formatting

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    Video    │ ──▶  │     SRT     │ ──▶  │     TXT     │ ──▶  │     MD      │ ──▶  │    DOCX    │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
   Video File        Subtitle File        Plain Text File       Markdown File       Word Document
```

Each step can be run independently or as part of the full pipeline.

## Folder Structure

```
linkedin-learning-pipeline/
├── app/                        # Application modules
│   ├── __init__.py            # Package initialization
│   ├── generate_srt.py        # Video to SRT transcription
│   ├── process_srt.py         # SRT to TXT conversion
│   ├── ai_summarizer.py       # Text summarization and processing
│   └── md2docx.py             # Markdown to DOCX conversion
├── config.py                  # Configuration utilities
├── config.yaml                # Configuration settings
├── main.py                    # Main entry point
├── pandoc-3.6.4-windows-x86_64.msi  # Pandoc installer
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

## Configuration

The application is configured through the `config.yaml` file. Key settings include:

### AI Model Configuration
```yaml
openai:
  model: "qwen2.5-7b-instruct-1m"
  temperature: 0.7
  api_key: "lm-studio"
  base_url: "http://10.16.17.42:1234/v1"
  max_tokens: 4000
  timeout: 60
```

### Processing Options
```yaml
processing:
  srt2txt:
    extract_text_only: true
    remove_timestamps: true
    combine_sentences: true
  txt2md:
    include_timestamps: false
    include_summary: true
    include_key_points: true
  md2docx:
    add_table_of_contents: true
    add_page_numbers: true
    template_file: ""
```

### UI Options
```yaml
ui:
  color_theme: "default"  # Options: default, dark, light, monochrome
  show_progress_bars: true
  show_spinners: true
```

## Troubleshooting

### Common Issues

1. **Missing dependencies**:
   - Ensure all required packages are installed with `pip install -r requirements.txt`
   - Verify Pandoc and FFmpeg are installed and accessible in your PATH

2. **GPU acceleration issues**:
   - Verify CUDA is properly installed for PyTorch
   - Check GPU compatibility with `torch.cuda.is_available()`

3. **Transcription quality issues**:
   - Try using a larger Whisper model (options: tiny, base, small, medium, large)
   - Improve audio quality of source videos

4. **Path errors**:
   - Use absolute paths when specifying input/output directories
   - Ensure proper permissions for reading/writing files

### Logs

Application logs are stored in the `logs` directory. Check these files for detailed error information when troubleshooting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Pandoc for document conversion
- OpenAI's Whisper for speech recognition
- PyTorch for machine learning functionality
