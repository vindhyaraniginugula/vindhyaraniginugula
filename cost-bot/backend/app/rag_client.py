import os
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# --- Env vars ---
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
AZURE_OPENAI_MODEL = os.environ.get("AZURE_OPENAI_MODEL", "gpt-35-turbo")

AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
AZURE_SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
AZURE_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]

# --- OpenAI client (new SDK) ---
openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-06-01",   # pinned version
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

# --- Azure Cognitive Search client ---
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY),
)


def retrieve_docs(question: str, top_k: int = 3):
    """Retrieve top K relevant documents from Azure Cognitive Search"""
    results = search_client.search(search_text=question, top=top_k)
    docs = []
    for r in results:
        content = r.get("content") or r.get("text") or str(r)
        docs.append(content)
    return docs


def generate_answer(question: str):
    """Retrieve relevant docs and query Azure OpenAI"""
    docs = retrieve_docs(question)
    prompt = f"""
You are an assistant summarizing Azure cost. 
Use the following documents to answer the question:

{chr(10).join(docs)}

Question: {question}
Answer concisely:
"""
    response = openai_client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,   # in new SDK use `model` not `deployment_name`
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content
