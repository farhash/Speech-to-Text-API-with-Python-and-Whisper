import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from timeit import default_timer as timer
import joblib

start_time = timer()


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "path_of_your_local_whisper_model"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)


end_time2 = timer()
print(f"after model to device : {end_time2-start_time:.3f} seconds")


processor = AutoProcessor.from_pretrained(model_id)

end_time3 = timer()
print(f"after processor : {end_time3-start_time:.3f} seconds")

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=15,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)  
end_time4 = timer()
print(f"after pipe : {end_time4-start_time:.3f} seconds") 

filename = "Completed_model.joblib"
joblib.dump(pipe, filename)


end_time = timer()
print(f"[INFO] Total training time: {end_time-start_time:.3f} seconds")
