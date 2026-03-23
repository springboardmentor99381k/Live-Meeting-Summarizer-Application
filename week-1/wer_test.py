from jiwer import Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces, Strip, wer

transformation = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

ref = open("EN2001a_reference.txt").read()
whisper_pred = open("whisper_output.txt").read()
vosk_pred = open("vosk_output.txt").read()

ref_clean = transformation(ref)
whisper_clean = transformation(whisper_pred)
vosk_clean = transformation(vosk_pred)

whisper_wer = wer(ref_clean, whisper_clean)
vosk_wer = wer(ref_clean, vosk_clean)

print("Whisper WER:", whisper_wer)
print("Vosk WER:", vosk_wer)
