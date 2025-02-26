import json
import pdfplumber
from pathlib import Path
from urllib.parse import quote  # <-- Added import

def extract_text(pdf_path):
    try:
        print(f"Processing: {pdf_path.name}")
        with pdfplumber.open(pdf_path) as pdf:
            return " ".join(page.extract_text() or "" for page in pdf.pages[:3])
    except Exception as e:
        print(f"Error with {pdf_path.name}: {str(e)}")
        return ""

def build_index():
    index = []
    allowed_dirs = {
       "olevel": {"cie": "olevel-cie", "edexcel": "olevel-edexcel"},
       "alevel": {"cie": "alevel-cie", "edexcel": "alevel-edexcel"}
    }

    # Add validation check
    for level, boards in allowed_dirs.items():
        for board, dir_name in boards.items():
            dir_path = Path(dir_name)
            if not dir_path.exists():
                print(f"⚠️ Missing folder: {dir_path}")
                continue
                
            print(f"\nScanning: {dir_path}")
            pdf_files = list(dir_path.glob("*.pdf"))
            
            if not pdf_files:
                print(f"  No PDFs found in {dir_path}")
                
            for i, pdf_file in enumerate(pdf_files, 1):
                print(f"  {i}/{len(pdf_files)}: {pdf_file.name}")
                content = extract_text(pdf_file)
                raw_path = str(pdf_file).replace("\\", "/")  # Windows paths
                encoded_path = quote(raw_path)  # URL encoding
                index.append({
                    "path": encoded_path,  # <-- Now URL-safe
                    "level": level,
                    "board": board,
                    "title": pdf_file.stem.replace("_", " ").replace("-", " ").title(),
                    "keywords": pdf_file.stem.lower().replace("_", " ").split(),
                    "content": " ".join(content.split()[:500])
                })

    with open("pdf_index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Success! Indexed {len(index)} PDFs")

if __name__ == "__main__":
    build_index()