import uuid
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view     
from stt.models import STTResult
from stt.serializers import STTSerializer
from stt.tasks import celery_stt
import logging
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from stt.forms import FileForm
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
User = get_user_model()
logger = logging.getLogger(__name__)


class SttGeneral(APIView):
	
	@extend_schema(
    	request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "audio_url": {"audio_url": "string"},
            	},
        	},
		},
    	responses={201: STTSerializer},
		description='[POST] Enter a link of an audio or video file',
	)
	def post(self, request: Request):

		data = request.data

		if "audio_url" not in data:
			logger.warning("Audio url doesn't exist")
			return Response(
				{"message": "'audio_url' Not Provided"}, status=status.HTTP_400_BAD_REQUEST
			)

		task = {}
		task["user"] = request.user.id 
		task["stt_result_key"] = uuid.uuid4().hex
		task["stt_result_status"] = "pending"
		task["stt_result_script"] = ""
		task["stt_start_time"] = timezone.now()
		task["stt_end_time"] = timezone.now()
		task["audio_source_url"] = data["audio_url"]
		serializer = STTSerializer(data=task)
		
		if serializer.is_valid():
			stt_task = serializer.save() 
			celery_stt.delay(stt_task.stt_result_key) 
			response = generateSTTResultResponse(stt_task)
			return Response(response, status=status.HTTP_200_OK)
		return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		
	
class SttDetail(APIView):
	@extend_schema(
    	responses={201: STTSerializer},
		description='[GET] Enter the result key in this field',
	)
	def post(self, request: Request, stt_result_key):
		try:
			stt_task = STTResult.objects.get(stt_result_key=stt_result_key)
		except STTResult.DoesNotExist:
			
			return Response(
				logger.warning("Key doesn't exist"), 
				{"message": "No matching STT task found"},
				status=status.HTTP_404_NOT_FOUND
			)

		if stt_task.user_id != request.user.id:
			return Response(
				{"message": "User is not the right owner of the stt task"},
				status=status.HTTP_403_FORBIDDEN,
			)

		response = generateSTTResultResponse(stt_task)
		return Response(response, status=status.HTTP_200_OK)


@extend_schema(
	request={
		'multipart/form-data': {
			'type': 'object',
			'properties': {
				'audio': {
					'type': 'string',
					'format': 'binary'
				}
			}
		}
	},
	responses={201: STTSerializer},
	description='[POST] Enter the audio file in this field',
)
@api_view(["POST"])
def upload_file(request: Request):

	form = FileForm(request.POST, request.FILES)
	if form.is_valid():
		saved_form = form.save()
		audio_path = saved_form.audio
		data = {}
		data["audio_url"] = f"{base_dir}/media/{audio_path}"
		print("data is: ", data)
		

	if "audio_url" not in data:
		logger.warning("Audio url doesn't exist")
		return Response(
			{"message": "'audio_url' Not Provided"}, status=status.HTTP_400_BAD_REQUEST
		)

	task = {}
	task["user"] = request.user.id 
	task["stt_result_key"] = uuid.uuid4().hex
	task["stt_result_status"] = "pending"
	task["stt_result_script"] = ""
	task["stt_start_time"] = timezone.now()
	task["stt_end_time"] = timezone.now()
	task["audio_source_url"] = data["audio_url"]
	serializer = STTSerializer(data=task)
	
	if serializer.is_valid():
		stt_task = serializer.save()
		celery_stt.delay(stt_task.stt_result_key) 
		response = generateSTTResultResponse(stt_task)
		return Response(response, status=status.HTTP_200_OK)
	return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
		

def generateSTTResultResponse(stt_task):
	response = {}
	response["stt_result_key"]     = stt_task.stt_result_key
	response["stt_result_status"]  = stt_task.stt_result_status
	response["stt_result_script"]  = stt_task.stt_result_script
	response["stt_start_time"]     = stt_task.stt_start_time
	response["stt_end_time"]       = stt_task.stt_end_time
	response["audio_source_url"]   = stt_task.audio_source_url
	return response 

#endregion
