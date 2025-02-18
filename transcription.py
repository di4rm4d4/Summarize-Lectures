import json
from transformers import pipeline
import os

OUTPUT_JSON = "transcription.json"  
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    if len(text) < 100:
        return text  
    summary = summarizer(text, max_length=200, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def summarize_transcription_from_json():
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        full_text = " ".join(data["transcription"])
    
    summary = summarize_text(full_text)
    print("\n🔹 **Summary:**")
    print(summary)
    return summary  # Ensure the summary is returned

def save_to_obsidian_vault(vault_path, note_title, note_content):
    note_path = os.path.join(vault_path, f"{note_title}.md")
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)
    print(f"Note saved to {note_path}")

if __name__ == "__main__":
    summary = summarize_transcription_from_json()
    vault_path = "a15fcf63dded4ece"  
    save_to_obsidian_vault(vault_path, "Summarized Transcription", summary)