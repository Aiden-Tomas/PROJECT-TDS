# scraper/course_scraper.py

import requests
import os
import json

BASE_URL = "https://tds.s-anand.net/"
OUTPUT_DIR = "../data/course_content/"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Hardcoded list of files (expandable later)
lecture_files = [
    "README.md",
    "_sidebar.md",
    "development-tools.md",
    "vscode.md",
    "github-copilot.md",
    "uv.md",
    "unicode.md",
    "devtools.md",
    "css-selectors.md",
    "json.md",
    "bash.md",
    "llm.md",
    "spreadsheets.md",
    "sqlite.md",
    "git.md",
    "deployment-tools.md",
    "markdown.md",
    "image-compression.md",
    "github-pages.md",
    "vercel.md",
    "colab.md",
    "github-actions.md",
    "github-codespaces.md",
    "docker.md",
    "ngrok.md",
    "cors.md",
    "rest-apis.md",
    "fastapi.md",
    "google-auth.md",
    "ollama.md",
    "large-language-models.md",
    "llm-evals.md",
    "llm-speech.md",
    "llm-image-generation.md",
    "llm-agents.md",
    "function-calling.md",
    "hybrid-rag-typesense.md",
    "rag-cli.md",
    "vector-databases.md",
    "topic-modeling.md",
    "multimodal-embeddings.md",
    "embeddings.md",
    "vision-models.md",
    "base64-encoding.md",
    "llm-text-extraction.md",
    "llm-sentiment-analysis.md",
    "tds-gpt-reviewer.md",
    "tds-ta-instructions.md",
    "prompt-engineering.md"
]

def scrape_course():
    all_data = []
    for file in lecture_files:
        url = f"{BASE_URL}{file}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            continue
        content = response.text
        all_data.append({"url": url, "content": content})
        print(f"Scraped {url}")

    with open(os.path.join(OUTPUT_DIR, "course_content.json"), "w") as f:
        json.dump(all_data, f, indent=2)

if __name__ == "__main__":
    scrape_course()