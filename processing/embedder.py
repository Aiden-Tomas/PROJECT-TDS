# processing/embedder.py

import json
import os
import openai
from dotenv import load_dotenv
from processing.chunker import clean_and_chunk
from vectordb.chroma_db import get_chroma_collection

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embeddings(texts):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [e['embedding'] for e in response['data']]

def process_and_store():
    collection = get_chroma_collection()

    # Load course content
    with open("../data/course_content/course_content.json") as f:
        course_data = json.load(f)

    for item in course_data:
        chunks = clean_and_chunk(item['content'])
        embeddings = get_embeddings(chunks)
        for chunk, emb in zip(chunks, embeddings):
            collection.add(
                documents=[chunk],
                embeddings=[emb],
                metadatas=[{"source": item['url']}],
                ids=[item['url'] + str(hash(chunk))]
            )

    # Load discourse content
    with open("../data/discourse/discourse.json") as f:
        discourse_data = json.load(f)

    for item in discourse_data:
        chunks = clean_and_chunk(item['content'])
        embeddings = get_embeddings(chunks)
        for chunk, emb in zip(chunks, embeddings):
            collection.add(
                documents=[chunk],
                embeddings=[emb],
                metadatas=[{"source": f"Topic {item['topic_id']}"}],
                ids=[str(item['topic_id']) + str(hash(chunk))]
            )

if __name__ == "__main__":
    process_and_store()
