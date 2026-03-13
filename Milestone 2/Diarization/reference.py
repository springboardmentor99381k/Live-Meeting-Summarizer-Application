import os
import xml.etree.ElementTree as ET

MEETING_ID = "ES2002a"
SEGMENTS_FOLDER = "segments"
MAX_TIME = 300.0  # 5 minutes

print("Creating full reference.rttm...")

with open("reference.rttm", "w") as rttm:

    for file in os.listdir(SEGMENTS_FOLDER):
        if file.startswith(MEETING_ID) and file.endswith(".xml"):

            speaker = file.split(".")[1]

            tree = ET.parse(os.path.join(SEGMENTS_FOLDER, file))
            root = tree.getroot()

            for segment in root.findall("segment"):
                start = float(segment.attrib["transcriber_start"])
                end = float(segment.attrib["transcriber_end"])
                duration = end - start

                rttm.write(
                    f"SPEAKER {MEETING_ID} 1 {start:.3f} {duration:.3f} <NA> <NA> {speaker} <NA> <NA>\n"
                )

print("Full reference.rttm created.")

print("Trimming to first 5 minutes...")

with open("reference.rttm", "r") as infile, open("reference_5min.rttm", "w") as outfile:
    for line in infile:
        parts = line.strip().split()

        start = float(parts[3])
        duration = float(parts[4])
        end = start + duration

        if start < MAX_TIME:
            if end > MAX_TIME:
                duration = MAX_TIME - start

            parts[4] = f"{duration:.3f}"
            outfile.write(" ".join(parts) + "\n")

print("reference_5min.rttm created successfully!")