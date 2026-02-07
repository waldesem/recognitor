# Recognitor

A simple application that converts speech to text.

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

3. **Install Vosk models (for offline recognition):**
```bash
wget https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip
unzip vosk-model-ru-0.42.zip
mv vosk-model-ru-0.42 model
rm vosk-model-ru-0.42.zip

# Code below not tested yet
wget https://alphacephei.com/vosk/models/vosk-recasepunc-ru-0.22.zip
unzip vosk-recasepunc-ru-0.22.zip
mv vosk-recasepunc-ru-0.22 recasepunc
rm vosk-recasepunc-ru-0.22.zip

wget https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip
unzip vosk-model-spk-0.4.zip
mv vosk-model-spk-0.4 spk
rm vosk-model-spk-0.4.zip
```

## Usage

1. **Run the application:**
```bash
python3 recognitor.py '/dest/audio-video.file'
```
Output file placed in the same directory as input file.

## Building Executable
You can create a standalone executable using PyInstaller that includes all dependencies and models.
```bash
pyinstaller --windowed --add-data="model:model" recognitor.py
```

## License

This project is licensed under the MIT License.