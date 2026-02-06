"""Recognition module."""

import io
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import camelot
import cv2
import numpy as np
import pandas as pd
import pymupdf
import pytesseract
from moviepy import AudioFileClip
from PIL import Image
from speech_recognition import AudioFile, Recognizer


class Recognitor:
    """GUI for recognition app."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI."""
        self.root = root
        self.root.title("Recognitor")
        self.root.geometry("540x260")

        # Variables
        self.input_file = None
        self.output_file = None
        self.file_types = [
            ("Portable Document Format", "*.PDF *.pdf"),
            ("Image files", "*.jpg *.jpeg *.png *.bmp"),
            ("Media files", "*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.ogg"),
        ]
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the UI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Recognitor",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # File selection
        ttk.Label(main_frame, text="Select file:").grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=5,
        )
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.file_label = ttk.Label(
            file_frame,
            text="No file selected",
            foreground="gray",
            width=50,
        )
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.upload_btn = ttk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file,
        )
        self.upload_btn.grid(row=0, column=1)

        # Checkbox
        self.checkbox_var = tk.BooleanVar()
        self.check_button = ttk.Checkbutton(
            main_frame,
            text="Pdf as images",
            variable=self.checkbox_var,
        )
        self.check_button.grid(
            row=3,
            column=0,
            sticky=tk.W,
            pady=(10, 0),
            padx=(0, 10),
            columnspan=2,
        )
        self.checkbox_var.set(False)

        # Progress bar
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=(20, 5))
        self.progress_bar = ttk.Progressbar(main_frame, mode="determinate")
        self.progress_bar.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E),
            pady=5,
        )

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)

    def browse_file(self) -> None:
        """Open file dialog to select file."""
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=self.file_types,
        )
        if filename:
            self.input_file = Path(filename)
            self.file_label.config(text=self.input_file.name, foreground="black")
            self.start_conversion()

    def start_conversion(self) -> None:
        """Start conversion process."""
        if self.input_file.suffix in self.file_types[0][1]:
            self.recogize_pdf()
        elif self.input_file.suffix in self.file_types[1][1]:
            self.recogize_image()
        elif self.input_file.suffix in self.file_types[2][1]:
            self.recogize_media()

    def conversion_completed(self) -> None:
        """Handle successful conversion completion."""
        self.progress_bar.stop()
        self.re_enable_button()
        messagebox.showinfo("Success", f"File saved as:\n{self.output_file.name}")
        self.open_folder()

    def conversion_failed(self, error_message: str) -> None:
        """Handle conversion failure."""
        self.progress_bar.stop()
        self.re_enable_button()
        messagebox.showerror("Error", f"Conversion failed:\n{error_message}")

    def re_enable_button(self) -> None:
        """Re-enable buttons."""
        self.input_file = None
        self.progress_label.config(text="")
        self.upload_btn.config(state="normal")
        self.file_label.config(text="No file selected", foreground="gray")

    def open_folder(self) -> None:
        """Open the folder containing the generated text file."""
        try:
            # Try to open folder with default system application
            if os.name == "nt":  # Windows
                os.startfile(self.output_file.parent)  # noqa: S606
            elif os.name == "darwin":  # macOS
                os.system(f'open "{self.output_file.parent}"')  # noqa: S605
            elif os.name == "posix":  # Linux
                os.system(f'xdg-open "{self.output_file.parent}"')  # noqa: S605
        except OSError as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    def recogize_pdf(self) -> None:
        """Extract data from a PDF file."""
        if self.checkbox_var:
            if texts := self.pdf_image_to_text():
                self.output_file = Path(
                    self.input_file.parent,
                    f"{self.input_file.stem}.txt",
                )
                with self.output_file.open("w", encoding="utf-8") as f:
                    for text in texts:
                        f.write(text)
                self.root.after(0, self.conversion_completed)
            else:
                self.conversion_failed("Failed to extract data from file")
        elif pages := self.pdf_table_to_excel():
            for i in range(0, len(pages), 100):
                self.pdf_to_excel(pages, i)
                self.merge_xlsx_files(self.input_file.parent)
                self.progress_bar.step(i)
            self.root.after(0, self.conversion_completed)
        else:
            self.conversion_failed("Failed to extract data from file")

    def pdf_table_to_excel(self) -> list:
        """Extract tables from a PDF file."""
        handler = camelot.handlers.PDFHandler(self.input_file)
        pages = handler._get_pages(pages="all")  # noqa: SLF001
        self.progress_bar["maximum"] = len(pages)
        return pages

    def recogize_image(self) -> None:
        """Extract data from an image file."""
        with Path.open(self.input_file, "rb") as file_input:
            if text := self.scan_image(file_input.read()):
                self.output_file = Path(
                    self.input_file.parent,
                    f"{self.input_file.stem}.txt",
                )
                with self.output_file.open("w", encoding="utf-8") as file_output:
                    file_output.write(text)
                self.root.after(0, self.conversion_completed)
            else:
                self.conversion_failed("Failed to extract data from image")

    def pdf_image_to_text(self) -> list:
        """Extract data from PDF image file into text file."""
        images = self.extract_images_from_pdf()
        self.progress_bar["maximum"] = len(images)
        tables = []
        for page_num, image_bytes in images:
            text = self.scan_image(image_bytes)
            tables.append(text)
            self.progress_bar.step(page_num)
        return tables

    def extract_images_from_pdf(self) -> list[tuple[int, bytes]]:
        """Extract images from a PDF file."""
        doc = pymupdf.open(self.input_file)
        images = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            for img in image_list:
                base_image = doc.extract_image(img[0])
                image_bytes = base_image["image"]
                images.append((page_num, image_bytes))
        return images

    @staticmethod
    def scan_image(image_bytes: bytes) -> str:
        """Preprocess the image for OCR."""
        image = Image.open(io.BytesIO(image_bytes))
        image = np.array(image.convert("L"))  # Перевод в grayscale
        _, binary = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)  # Бинаризация
        text: str = pytesseract.image_to_string(
            binary,
            lang="rus+eng'",
            config="--psm 6",
        )
        return text

    def pdf_to_excel(self, page_list: list, i: int) -> None:
        """Convert a range of pages from a PDF file to Excel format."""
        pages = ", ".join([str(page) for page in page_list[i : i + 100]])
        tables = camelot.read_pdf(self.input_file, pages=pages)

        df = pd.concat([table.df for table in tables], ignore_index=True)

        df.to_excel(
            Path(
                self.input_file.parent,
                self.input_file.replace(".pdf", f"_{i // 100 + 1}.xlsx"),
            ),
            sheet_name="Sheet1",
            index=False,
        )

    def merge_xlsx_files(self, pdf_file_path: Path) -> None:
        """Merge multiple partially converted Excel files into one Excel file."""
        dfs = []
        for xlsx_file_path in sorted(Path(self.input_file.parent).iterdir()):
            if xlsx_file_path.match(
                pdf_file_path.replace(".pdf", "_"),
            ) and xlsx_file_path.suffix(".xlsx"):
                df = pd.read_excel(
                    Path(self.input_file.parent, xlsx_file_path),
                )
                dfs.append(df)

                Path.unlink(Path(self.input_file.parent, xlsx_file_path))

        combined_df = pd.concat(dfs, ignore_index=True)
        headers = [f"column_{index}" for index, _ in enumerate(combined_df.columns)]
        combined_df.columns = headers

        final_df = combined_df.replace("\n", " ", regex=True)
        final_df.to_excel(
            Path(self.input_file.parent, pdf_file_path.replace(".pdf", ".xlsx")),
            sheet_name="Sheet1",
            index=False,
        )
        messagebox.showinfo("Merged in Excel format.")

    def recogize_media(self) -> None:
        """Convert media to text."""
        try:
            # Load the media file. Extract/convert the audio
            self.progress_bar.step(30)
            self.root.after(
                0,
                lambda: self.progress_label.config(text="Extracting audio..."),
            )
            file = AudioFileClip(str(self.input_file))
            wav_filename = self.input_file.parent / f"{self.input_file.stem}.wav"
            file.write_audiofile(str(wav_filename))
            file.close()

            # Initialize recognizer
            self.progress_bar.step(30)
            self.root.after(
                0,
                lambda: self.progress_label.config(text="Converting speech to text..."),
            )
            r = Recognizer()
            with AudioFile(str(wav_filename)) as source:
                data = r.record(source)
                text = r.recognize_vosk(data)

            # Save text to file
            self.progress_bar.step(30)
            self.output_file = self.input_file.parent / f"{self.input_file.stem}.txt"
            with self.output_file.open("w", encoding="utf-8") as f:
                f.write(text)

            # Update UI on completion
            if wav_filename.exists():
                wav_filename.unlink()
            self.root.after(0, self.conversion_completed)

        except Exception as e:  # noqa: BLE001
            error_message = str(e)
            self.root.after(0, lambda msg=error_message: self.conversion_failed(msg))


def main() -> None:
    """Run the application."""
    root = tk.Tk()
    Recognitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
