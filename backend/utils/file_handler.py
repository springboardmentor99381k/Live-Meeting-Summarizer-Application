import tempfile
import subprocess
import os
# async def save_temp_file(file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
#         temp.write(await file.read())
#         return temp.name
async def save_temp_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp:
        temp.write(await file.read())
        input_path =  temp.name

    output_path = input_path.replace(".webm", ".wav")

    subprocess.run([
        "ffmpeg",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path
    ])

    return output_path