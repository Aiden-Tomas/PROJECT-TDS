import os
import json
import requests
from dotenv import load_dotenv
from urllib.parse import unquote

# Load cookies from .env
load_dotenv()
T_COOKIE = unquote(os.getenv("DISCOURSE_T_COOKIE", ""))
FORUM_SESSION = unquote(os.getenv("DISCOURSE_FORUM_SESSION", ""))

if not T_COOKIE or not FORUM_SESSION:
    raise ValueError("❌ Missing one or both cookies in .env")

# Constants
BASE_DOMAIN = "discourse.onlinedegree.iitm.ac.in"
BASE_URL = f"https://{BASE_DOMAIN}/c/courses/tds-kb/34"
OUTPUT_PATH = "data/discourse_posts.json"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Create session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Referer": f"https://{BASE_DOMAIN}/",
    "Origin": f"https://{BASE_DOMAIN}"
})
session.cookies.set("_t", T_COOKIE, domain=BASE_DOMAIN)
session.cookies.set("_forum_session", FORUM_SESSION, domain=BASE_DOMAIN)

def get_topic_urls():
    topic_urls = []
    for page in range(0, 20):
        url = f"{BASE_URL}.json?page={page}"
        response = session.get(url)
        if response.status_code == 403:
            print(f"❌ 403 Forbidden on page {page} — check if cookies expired")
            continue
        elif response.status_code != 200:
            print(f"❌ Failed to fetch page {page}: HTTP {response.status_code}")
            continue

        data = response.json()
        for topic in data.get("topic_list", {}).get("topics", []):
            topic_urls.append((topic["id"], topic["slug"]))
    return topic_urls

def scrape_posts():
    all_posts = []
    topic_urls = get_topic_urls()

    for topic_id, slug in topic_urls:
        url = f"https://{BASE_DOMAIN}/t/{slug}/{topic_id}.json"
        response = session.get(url)
        if response.status_code == 403:
            print(f"❌ 403 on topic {topic_id} — likely expired session")
            continue
        elif response.status_code != 200:
            print(f"❌ Failed to fetch topic {topic_id}: {response.status_code}")
            continue

        data = response.json()
        for post in data["post_stream"]["posts"]:
            all_posts.append({
                "topic_id": topic_id,
                "title": data["title"],
                "post_number": post["post_number"],
                "content": post["cooked"],
                "username": post["username"]
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(all_posts)} posts.")

if __name__ == "__main__":
    scrape_posts()
