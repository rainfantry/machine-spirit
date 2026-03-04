import docx
import os

def extract_text(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading {file_path}: {e}"

files = [
    r"C:\Users\veren\OneDrive\Desktop\drills\CSHARP_FIELD_MANUAL.docx",
    r"C:\Users\veren\OneDrive\Desktop\drills\CSHARP_PRACTICE_WORKBOOK.docx"
]

for file_path in files:
    if os.path.exists(file_path):
        print(f"--- CONTENT OF {os.path.basename(file_path)} ---")
        print(extract_text(file_path))
        print("\n" + "="*50 + "\n")
    else:
        print(f"File not found: {file_path}")
