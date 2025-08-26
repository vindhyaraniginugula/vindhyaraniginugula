from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://<your-static-site>.azurestaticapps.net"],  # update later
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True,
)

@app.post("/ask")
async def ask(payload: dict):
    question = payload.get("question")
    # call your RAG search + OpenAI code here using env vars or KeyVault
    return {"answer": "placeholder answer for: " + question}
