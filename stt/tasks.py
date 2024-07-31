from django.utils import timezone
from .models import STTResult
from stt_api.celery import app
import logging
import re   
import subprocess
import soundfile as sf
import os
from pydub import AudioSegment
import tempfile
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import gc

 
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def process_chunk(model, processor, signal, rate):
    input_features = processor(signal, return_tensors='pt', sampling_rate=rate).input_features.to('cuda')
    output = model.generate(input_features)
    transcription = processor.decode(output[0], skip_special_tokens=False, normalize=False)
    return transcription

def resample_audio(input_file, output_file, sample_rate='16000'):
    subprocess.run(['ffmpeg', '-y', '-i', input_file, '-ar', sample_rate, '-ac', '1',  output_file])

@app.task(queue="stt_task")
def celery_stt(stt_result_key):
    try:
        stt_task = STTResult.objects.get(stt_result_key=stt_result_key)
    except STTResult.DoesNotExist as e:
        markAsFailed(stt_task)
        logger.warning("Key doesn't exist", e)
        return
    
    file_path = stt_task.audio_source_url
    
    if not isValidUrl(file_path):
        logger.warning("Not valid URL")
        markAsFailed(stt_task)
        return
    
    try:
        processor = WhisperProcessor.from_pretrained("/media/farhat/4cde39e4-2700-4061-a127-7c28b1cd563c/arshiya/models/whisper-medium-ASR-finetune")
        model = WhisperForConditionalGeneration.from_pretrained("/media/farhat/4cde39e4-2700-4061-a127-7c28b1cd563c/arshiya/models/whisper-medium-ASR-finetune", from_tf=False)
        temp_file = tempfile.NamedTemporaryFile(dir="./temps", delete=False, suffix=".wav").name

        resample_audio(file_path, temp_file)
        signal, rate = sf.read(temp_file)

        chunk_length_ms = 25 * 1000
        audio = AudioSegment.from_file(temp_file)
        chunks = []
        for i in range(0, len(audio), chunk_length_ms):
            chunks.append(audio[i:i + chunk_length_ms])
        full_transcription = ""
        model = model.to('cuda')
        model.eval()
        for i, chunk in enumerate(chunks):
            chunk.export(temp_file, format="wav")
            signal, rate = sf.read(temp_file)
            transcription = process_chunk(model, processor, signal, rate)
            full_transcription += transcription + " "
            os.remove(temp_file)

        clean_text = re.sub(r'<.*?>', '', full_transcription).strip()
        del model
        del processor
        torch.cuda.empty_cache()
        gc.collect()
        torch.cuda.synchronize()
    except Exception as e:
        torch.cuda.empty_cache()
        logger.warning("couldn't transcribe, ", e)
        markAsFailed(stt_task)
        return
    
    stt_task.stt_result_script  = clean_text
    stt_task.stt_result_status  = "success"
    stt_task.stt_end_time       = timezone.now()
    stt_task.save()  

def isValidUrl(audio_url):
    acceptable_formats = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    for format in acceptable_formats:
        if audio_url.endswith(format): return True
    return False

def markAsFailed(stt_task):
    logger.warning("Exception occurred")
    stt_task.stt_result_status = "failed"
    stt_task.stt_end_time      = timezone.now()
    stt_task.save()

def empty_cache():
    torch.cuda.empty_cache()
