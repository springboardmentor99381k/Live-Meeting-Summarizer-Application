import xml.etree.ElementTree as ET
import re

reference_files = [
    "ES2002a.A.words.xml",
    "ES2002a.B.words.xml",
    "ES2002a.C.words.xml",
    "ES2002a.D.words.xml"
]

all_words = []

for file in reference_files:
    tree = ET.parse(file)
    root = tree.getroot()

    for word in root.iter('w'):
        if word.text and word.get("starttime"):
            start_time = float(word.get("starttime"))

            # ONLY first 180 seconds
            if start_time <= 180:
                text = word.text.lower()
                all_words.append((start_time, text))

# Sort by global time
all_words.sort(key=lambda x: x[0])

ordered_words = [word for _, word in all_words]

clean_text = " ".join(ordered_words)

# Normalize
clean_text = re.sub(r"[^\w\s]", "", clean_text)
clean_text = re.sub(r"\s+", " ", clean_text)
clean_text = clean_text.strip()

with open("reference.txt", "w", encoding="utf-8") as f:
    f.write(clean_text)

print("Trimmed multi-speaker reference created!")