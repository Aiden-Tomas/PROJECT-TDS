# processing/chunker.py

import re

# Very simple chunker for now (can upgrade later)
def clean_and_chunk(text, chunk_size=500):
    # Remove HTML tags (for discourse)
    clean = re.sub('<[^<]+?>', '', text)
    clean = re.sub('\s+', ' ', clean).strip()

    # Chunking
    chunks = []
    for i in range(0, len(clean), chunk_size):
        chunks.append(clean[i:i+chunk_size])

    return chunks
