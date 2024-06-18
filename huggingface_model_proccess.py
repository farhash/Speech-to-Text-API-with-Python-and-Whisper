''' if you wanna use your models from huggingface,
    replace your address with address in processor and model section '''

from transformers import WhisperProcessor, WhisperForConditionalGeneration
from evaluate import load
import torch


metric = load("wer")
access_key = "your access key"
processor = WhisperProcessor.from_pretrained("huggingface_address", token=access_key)
model = WhisperForConditionalGeneration.from_pretrained("huggingface_address", token=access_key)

processor.save_pretrained("./saved_model")
model.save_pretrained("./saved_model")

''' and replace the following lines with the current model in tasks.py'''


# from transformers import WhisperProcessor, WhisperForConditionalGeneration
# import librosa
# import torch
# import subprocess
# import soundfile as sf
# import os

# processor = WhisperProcessor.from_pretrained("./saved_model")
# model = WhisperForConditionalGeneration.from_pretrained("./saved_model", from_tf=False)

# path = audio_url

# signal, rate = librosa.load(path)

# def resample_audio(input_file, output_file, sample_rate='16000'):
#     subprocess.run(['ffmpeg', '-i', input_file, '-ar', sample_rate, '-ac', '1',  output_file]) 
# if rate != 16000:
#     resample_audio(path, './temp.wav')
# signal, rate = sf.read('./temp.wav')

# model = model.to('cuda')
# model.eval()
# with torch.no_grad():
#     input_features = processor(signal, return_tensors='pt', sampling_rate=rate).input_features.to('cuda')
#     output = model.generate(input_features)
#     result = processor.decode(output[0], skip_special_tokens=True, normalize=True)

# os.remove("/home/farhat/Desktop/nevisa_api/temp.wav")