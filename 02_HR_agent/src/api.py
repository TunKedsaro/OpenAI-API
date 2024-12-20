from typing import Union
from fastapi import FastAPI

import os
from pydantic import BaseModel
from typing import Optional,Dict
from fastapi.middleware.cors import CORSMiddleware
import openai  
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

print("Import Done!!!")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

chef_email = """
Dear Hiring Manager,
I am writing to express my interest in the Head Chef position at KBTG. With over 15 years of culinary experience, including 5 years as Executive Chef at renowned restaurants, I am confident in my ability to contribute to your esteemed establishment.
My expertise in diverse cuisines, team leadership, and innovative menu development align well with the vision of KBTG. I am excited about the opportunity to bring my passion for culinary excellence to your team.
Please find my resume attached for your review. I look forward to the possibility of discussing how my background, skills, and certifications can be an asset to KBTG.
Thank you for considering my application.
Sincerely,
Aroii Dee
"""

# Step 01: Email Data Extraction
email_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
            """
            You are a Hiring Manager at KBTG reading a candidate's email.
            A candidate's email text will be given.
            Your task is to identify the following information and convert it into a JSON object with these keys:
            - job_position : string, the job position which the candidate is applying for.
            - company_name : string, the company name which the candidate is applying for.
            - candidate_name : string, the candidate name
            Answer in the form of a JSON object
            """),
        ("user",
            "{email}")
    ]
)
email_extraction_model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0
)
email_extraction_parser = JsonOutputParser()
email_extraction_chain = email_extraction_prompt | email_extraction_model | email_extraction_parser

# Step 02: Pass or NotPass Decision
def clean(text):
    return text.lower().strip().replace(" ", "")

def make_decision(candidate_data: Dict[str, str]) -> bool:
    opening_positions = ["Frontend Developer", "Backend Developer", "AI Developer", "Blockchain Developer"]
    opening_positions = set([clean(e) for e in opening_positions])
    criteria_1 = clean(candidate_data["job_position"]) in opening_positions
    criteria_2 = clean(candidate_data["company_name"]) == clean("KBTG")
    return criteria_1 and criteria_2

# Step 03: Response Email Generation
response_email_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
        """
        You are a Hiring Manager named "Khunthong Smith".
        Your task is to write an email response to a candidate's job application.
        """),
        ("user",
        """
        Write the response email in formal English language which notifies candidate name \"{candidate_name}\" that they \"{result}\".
        """)
    ]
)

response_email_model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=1.0
)

response_email_parser = StrOutputParser()
response_email_chain = response_email_prompt | response_email_model | response_email_parser

# Full Pipeline Function
def process_email_pipeline(email: str) -> str:
    # Step 01: Extract Data
    candidate_data = email_extraction_chain.invoke({"email": email})
    
    # Step 02: Make Decision
    is_pass = make_decision(candidate_data)
    result = "Pass" if is_pass else "Not_Pass"
    
    # Step 03: Generate Response Email
    response_email = response_email_chain.invoke(
        {
            "candidate_name": candidate_data["candidate_name"],
            "result": result
        }
    )
    return response_email

class EmailRequest(BaseModel):
    email: str
    
app = FastAPI()

@app.get("/")
async def health_check():
    return {"status":"ok","version":"2.0.0"}


@app.post("/step1")
async def test(request: EmailRequest):
    # result = {"status":"ok"}
    rp = process_email_pipeline(request.email)
    return {"result": rp}


