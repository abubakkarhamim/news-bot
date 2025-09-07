import os
from llmlayer import LLMLayerClient
import requests

LLMLAYER_API_KEY = os.environ["LLMLAYER_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]



client = LLMLayerClient(
    api_key= LLMLAYER_API_KEY,
)

response = client.search(
    query="at first mentioned everyone '@everyone'. search top 10 today news about bangladesh. the combined message shouldn't exceed 1900 characters",
    model="groq/llama-4-maverick-17b-128e-instruct",
    domain_filter=["dhakatribune.com", "thedailystar.net", "tbsnews.net",],
    return_sources= False,
    location='bd',
    response_language='en',
    max_tokens=480,
    date_filter="day",
    search_type = "news"
   

)

print(response.llm_response)
news_content = response.llm_response

# Print Source
# for source in response.sources:
#     print(f"- {source['title']}: {source['link']}")



# markdown_content = f"**LLMLayer Response:**\n{response.llm_response}\n\n**Sources:**\n"

# Send to Discord
discord_response = requests.post(
    DISCORD_WEBHOOK_URL,
    json={"content": news_content,
          }
)

# Optional: check if it worked
if discord_response.status_code == 204:
    print("News sent to Discord successfully!")
else:
    print(f"Failed to send to Discord. Status code: {discord_response.status_code}")
