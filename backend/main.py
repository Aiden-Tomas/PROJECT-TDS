import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Welcome! Use POST /api/ with a JSON body like {'question': 'your question'}"}
# Load course content JSON
if not os.path.exists("data/course_content/course_content.json"):
    raise FileNotFoundError("Run the scraper to generate course_content.json first.")

with open("data/course_content/course_content.json", "r", encoding="utf-8") as f:
    course_data = json.load(f)

texts = [entry["content"] for entry in course_data]
urls = [entry["url"] for entry in course_data]

EMBED_FILE = "data/course_content/embeddings.npy"
if os.path.exists(EMBED_FILE):
    print("Loading cached embeddings...")
    embeddings = np.load(EMBED_FILE)
else:
    print("Computing embeddings...")
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8192]
        )
        embeddings.append(response.data[0].embedding)
    embeddings = np.array(embeddings)
    np.save(EMBED_FILE, embeddings)

class Query(BaseModel):
    question: str

@app.post("/api/")
async def query_api(q: Query):
    question = q.question

    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    sims = cosine_similarity([query_emb], embeddings)[0]
    top_indices = sims.argsort()[::-1][:3]

    top_texts = [texts[i] for i in top_indices]
    top_urls = [urls[i] for i in top_indices]

    context = "\n---\n".join(top_texts)

    completion = client.chat.completions.create(
        model="openai/gpt-4.1-nano",
        messages=[
            {"role": "system", "content": f"Use the following context to answer:\n{context}"},
            {"role": "user", "content": question}
        ]
    )

    answer = completion.choices[0].message.content

    links = [
        {"url": url, "text": url.split('/')[-1].replace('-', ' ').replace('.md', '').title()}
        for url in top_urls
    ]

    return {"answer": answer, "links": links}
