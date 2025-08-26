import os
from azure.ai.openai import OpenAIClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -----------------------------
# Configuration
# -----------------------------
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")

# -----------------------------
# Initialize Clients
# -----------------------------
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

openai_client = OpenAIClient(endpoint=AZURE_OPENAI_ENDPOINT, credential=AzureKeyCredential(AZURE_OPENAI_KEY))

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    question = request.question

    # 1️⃣ Retrieve relevant docs from Azure AI Search
    try:
        search_results = search_client.search(
            query=question,
            top=5  # retrieve top 5 relevant docs
        )
        context_texts = [doc['content'] for doc in search_results]
        context = "\n".join(context_texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search Error: {str(e)}")

    # 2️⃣ Prepare the system + user prompt
    system_prompt = """
    You are a financial assistant chatbot for the leadership team.
    Answer questions based on the provided context from Azure cost data.
    Summarize costs, trends, and anomalies in an executive-friendly way.
    """
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

    # 3️⃣ Call Azure OpenAI
    try:
        response = openai_client.chat_completions.create(
            deployment_id="gpt-4",  # replace with your deployed model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500
        )
        answer = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

    return {"answer": answer}

# -----------------------------
# Run: uvicorn main:app --reload
# -----------------------------
