from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from datetime import timedelta
from typing import List
import whisper
import os

app = FastAPI()

# Load Whisper model
model = whisper.load_model("tiny")


# Configure CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],  # Adjust according to your frontend's URL
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.post("/transcribe/")
async def transcribe(files: List[UploadFile] = File(...)):
	transcriptions = {}
	for file in files:
		file_location = f"temp/{file.filename}"
		with open(file_location, "wb+") as file_object:
			file_object.write(file.file.read())
		result = model.transcribe(file_location)
		transcriptions[file.filename] = {
			'text': result['text'],
			'json': result,  # Assuming result is already a JSON-like dictionary
			'srt': convert_to_srt(result['segments'])  # Convert the text to SRT format
		}
		os.remove(file_location)  # Clean up the file after processing
	return JSONResponse(content=transcriptions)

def convert_to_srt(segments):
	# Simple mock SRT conversion
	full_segment = ""
	for segment in segments:
		startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
		endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
		text = segment['text']
		segmentId = segment['id']+1
		segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
		full_segment += segment
	return full_segment

@app.get("/")
async def root():
	return {"message": "Whisper API is running"}
