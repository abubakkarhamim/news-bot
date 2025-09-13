import os
from llmlayer import LLMLayerClient
import requests
import time

LLMLAYER_API_KEY = os.environ["LLMLAYER_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]



client = LLMLayerClient(
    api_key= LLMLAYER_API_KEY,
)

response = client.search(
    query="top 10 news about Bangladesh with detailed description",
    model="groq/llama-4-maverick-17b-128e-instruct",
    domain_filter=["dhakatribune.com", "thedailystar.net", "tbsnews.net",],
    return_sources= True,
    location='bd',
    response_language='en',
    max_tokens=2000,
    date_filter="day",
    search_type = "news"
   

)
print(response.llm_response)
news_content = response.llm_response

# 1. Break the content into chunks
max_chars = 1950  # Keep it under 2000 to be safe
chunks = []
current_chunk = ""

for line in news_content.split('\n'):
    if len(current_chunk) + len(line) + 1 > max_chars:
        chunks.append(current_chunk)
        current_chunk = ""
    current_chunk += line + "\n"

if current_chunk:
    chunks.append(current_chunk)

# 2. Send each chunk to Discord one by one
for i, chunk in enumerate(chunks):
    # Skip sending if the chunk is empty or just whitespace
    if not chunk.strip():
        print(f"Skipping empty chunk {i+1}/{len(chunks)}.")
        continue

    print(f"Sending chunk {i+1}/{len(chunks)} to Discord...")
    try:
        discord_response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": chunk}
        )
        discord_response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        print(f"Chunk {i+1} sent successfully!")

    except Exception as e:
        print(f"An unexpected error occurred while sending chunk {i+1}. Error: {e}")
    
    time.sleep(1) # Wait 1 second between messages to avoid rate limiting

# 3. Also send the sources at the end
if response.sources:
    source_content = "**Sources:**\n"
    for source in response.sources:
        # Check if source is a dictionary and has the required keys
        if isinstance(source, dict) and 'title' in source and 'link' in source:
            source_content += f"- {source['title']}: <{source['link']}>\n"
        else:
            print(f"Skipping malformed source item: {source}")

    # Check if sources list itself is too long and send
    if len(source_content) > len("**Sources:**\n"):
        print("Sending sources to Discord...")
        try:
            discord_response = requests.post(DISCORD_WEBHOOK_URL, json={"content": source_content})
            discord_response.raise_for_status()
            print("Sources sent to Discord.")
        except Exception as e:
            print(f"An unexpected error occurred while sending sources. Error: {e}")
