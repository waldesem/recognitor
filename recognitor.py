"""Recognition module."""

from pathlib import Path

import click
from moviepy import AudioFileClip
from speech_recognition import AudioFile, Recognizer


@click.command()
@click.argument(
    "input_file", type=click.Path(exists=True, file_okay=True, path_type=Path)
)
def speech_to_text(input_file: Path) -> None:
    """Recognize speech from an audio file and save it as text."""
    file = AudioFileClip(str(input_file))
    wav_filename = input_file.parent.joinpath(f"{input_file.stem}.wav")
    file.write_audiofile(str(wav_filename))
    file.close()

    # Initialize recognizer
    click.secho(
        f"Recognizing speech from {input_file.name}...",
        fg="green",
    )
    r = Recognizer()
    with AudioFile(str(wav_filename)) as source:
        data = r.record(source)
        text = r.recognize_vosk(data)

    # Save text to file
    output_file = input_file.parent.joinpath(f"{input_file.stem}.txt")
    with output_file.open("w", encoding="utf-8") as f:
        f.write(text)

    # Clean up temporary WAV file
    if wav_filename.exists():
        wav_filename.unlink()

    click.secho(
        f"Recognition complete. Text saved to {output_file.name}",
        fg="green",
    )


if __name__ == "__main__":
    speech_to_text()
