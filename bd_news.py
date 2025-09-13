import os
from llmlayer import LLMLayerClient
import requests

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

# 1. Save the full response to output.txt
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(news_content)
print("News content saved to output.txt")

# 2. Break the content into chunks
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

# 3. Send each chunk to Discord one by one
for i, chunk in enumerate(chunks):
    print(f"Sending chunk {i+1}/{len(chunks)} to Discord...")
    discord_response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": chunk}
    )

    if discord_response.status_code in [200, 204]:
        print(f"Chunk {i+1} sent successfully!")
    else:
        print(f"Failed to send chunk {i+1}. Status code: {discord_response.status_code}, Response: {discord_response.text}")
    
    time.sleep(1) # Wait 1 second between messages to avoid rate limiting

# 4. Also send the sources at the end
if response.sources:
    source_content = "**Sources:**\n"
    for source in response.sources:
        # Format as: - Title: <link>
        source_content += f"- {source['title']}: <{source['link']}>\n"

    # Check if sources list itself is too long and send
    if len(source_content) > 0:
        print("Sending sources to Discord...")
        requests.post(DISCORD_WEBHOOK_URL, json={"content": source_content})
        print("Sources sent to Discord.")
