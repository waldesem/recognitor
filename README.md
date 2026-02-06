# Recognitor

A simple Python GUI application that converts files to text.

## Features

- **Easy-to-use GUI** - Simple tkinter-based interface
- **Multiple media formats** - Supports MP4, AVI, MOV, MKV, MP3, WAV, OGG.
- **Portable Document Format** - Supports pdf tables, text and images.
- **Image formats** - Supports JPG, JPEG, PNG, BMP.
- **Real-time progress tracking** - Visual progress bar with status updates
- **Automatic file management** - Saves text files in the same directory as source
- **Cross-platform compatibility** - Works on Windows and Linux

## Screenshots

![Application Interface](screenshot.png)

## Requirements

- Python 3.12+
- vosk model (for offline speech recognition)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/waldesem/recognitor
cd recognitor
```

2. **Install required dependencies:**
```bash
pip install -r requirements.txt
```
NOTE: If problem `ModuleNotFoundError: No module named 'frontend'` appears after start app,
please execute commands:

```
pip uninstall fitz
pip install --force-reinstall pymupdf
```

3. **Install Vosk models (for offline recognition):**
```bash
wget https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip
unzip vosk-model-ru-0.42.zip
mv vosk-model-ru-0.42 model
```

## Usage

1. **Run the application:**
```bash
python recognitor.py
```

2. **Convert to text:**
   - Click "Browse" to select a file
   - Click "Convert to Text"
   - Wait for the conversion to complete
   - Click "Open Folder" to view the generated text file

## Building Executable
You can create a standalone executable using PyInstaller that includes all dependencies and models.
```bash
pyinstaller --windowed --add-data="model:model" recognitor.py
```

## License

This project is licensed under the MIT License.