from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit, QLabel, QFileDialog
import sys
import threading

from transcribeSummarize import transcribe_audio, save_transcription_to_json, transcribed_text
from summarizeTranscription import summarize_transcription_from_json, save_to_obsidian_vault

class LectureTranscriber(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lecture AI - Live Transcription & Notes")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.transcriptBox = QTextEdit(self)
        self.transcriptBox.setPlaceholderText("Live transcript will appear here...")
        self.layout.addWidget(self.transcriptBox)

        self.vaultPathLabel = QLabel("Obsidian Vault Path:")
        self.layout.addWidget(self.vaultPathLabel)
        self.vaultPathInput = QLineEdit(self)
        self.layout.addWidget(self.vaultPathInput)

        self.selectVaultPathButton = QPushButton("Select Vault Path")
        self.selectVaultPathButton.clicked.connect(self.select_vault_path)
        self.layout.addWidget(self.selectVaultPathButton)

        self.startTranscriptionButton = QPushButton("Start Transcription")
        self.startTranscriptionButton.clicked.connect(self.start_transcription)
        self.layout.addWidget(self.startTranscriptionButton)

        self.stopTranscriptionButton = QPushButton("Stop Transcription")
        self.stopTranscriptionButton.clicked.connect(self.stop_transcription)
        self.layout.addWidget(self.stopTranscriptionButton)

        self.summarizeButton = QPushButton("Summarize Transcription")
        self.summarizeButton.clicked.connect(self.summarize_transcription)
        self.layout.addWidget(self.summarizeButton)

        self.setLayout(self.layout)

        self.transcription_thread = None
        self.transcribing = False

    def select_vault_path(self):
        vault_path = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault Directory")
        if vault_path:
            self.vaultPathInput.setText(vault_path)

    def start_transcription(self):
        if not self.transcribing:
            self.transcribing = True
            self.transcription_thread = threading.Thread(target=self.run_transcription, daemon=True)
            self.transcription_thread.start()

    def run_transcription(self):
        transcribe_audio(self.update_transcript_box)

    def update_transcript_box(self, text):
        self.transcriptBox.append(text)

    def stop_transcription(self):
        if self.transcribing:
            self.transcribing = False
            save_transcription_to_json(transcribed_text)
            print("\n⏹️ Stopped listening.")
            self.transcription_thread = None

    def summarize_transcription(self):
        threading.Thread(target=self.run_summarization, daemon=True).start()

    def run_summarization(self):
        summary = summarize_transcription_from_json()
        self.transcriptBox.append("\n📌 **Summary:** " + summary)
        vault_path = self.vaultPathInput.text()
        save_to_obsidian_vault(vault_path, "Summarized Transcription", summary)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LectureTranscriber()
    window.show()
    sys.exit(app.exec())