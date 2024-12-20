from typing import Union
from fastapi import FastAPI

import os
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import openai  # Correct import statement
from dotenv import load_dotenv
print("Import Done!!!")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

class GrammarTaskRequest(BaseModel):
    text:str
    style:Optional[str] = "default"

class GrammarTaskResponse(BaseModel):
    text:str

@app.get("/")
async def health_check():
    return {"status":"ok","version":"2.0.0"}

@app.post("/openai/gramma", response_model=GrammarTaskResponse)
async def openai_grammar(request:GrammarTaskRequest)->GrammarTaskResponse:
    result_text = f"Processed text: {request.text}"
    return GrammarTaskResponse(text=result_text)