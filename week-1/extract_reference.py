import os
import xml.etree.ElementTree as ET

words_folder = "ami_public_manual_1.6.2/words"
meeting_id = "EN2001a"

all_words = []

for file in os.listdir(words_folder):
    if file.startswith(meeting_id):
        tree = ET.parse(os.path.join(words_folder, file))
        root = tree.getroot()

        for word in root.iter("w"):
            text = word.text
            start = word.attrib.get("starttime")

            if text and start:
                try:
                    start = float(start)
                    all_words.append((start, text.lower()))
                except:
                    pass

all_words.sort(key=lambda x: x[0])

reference_text = " ".join([word for _, word in all_words])

with open("EN2001a_reference.txt", "w", encoding="utf-8") as f:
    f.write(reference_text)

print("Chronologically ordered reference transcript saved.")
