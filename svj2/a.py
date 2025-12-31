import os
import pyperclip

directory = os.path.dirname(os.path.abspath(__file__))
wav_files = [f for f in os.listdir(directory) if f.lower().endswith(".ogg")]

result = "\n".join(wav_files)
pyperclip.copy(result)

print(f"Copied {len(wav_files)} filenames to clipboard.")
