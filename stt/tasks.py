from django.utils import timezone
from .models import STTResult
from stt_api.celery import app
import logging
import joblib


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.task(queue="stt_task")
def celery_stt(stt_result_key):
 
    try:
        stt_task = STTResult.objects.get(stt_result_key=stt_result_key)
    except STTResult.DoesNotExist as e:
        markAsFailed(stt_task)
        logger.warning("Key doesn't exist", e)
        return
    
    audio_url = stt_task.audio_source_url
    
    if not isValidUrl(audio_url):
        logger.warning("Not valid URL")
        markAsFailed(stt_task)
        return
    
    loaded_model_joblib = joblib.load('Completed_model.joblib')

    try:
        result = loaded_model_joblib(audio_url)

    except Exception as e:
        logger.warning("couldn't transcribe, ", e)
        markAsFailed(stt_task)
        return
    
    stt_task.stt_result_script  = result['text']
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