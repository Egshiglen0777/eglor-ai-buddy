from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow requests from Carrd
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify Carrd's domain)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Use Railway environment variable for the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
async def chat_with_eglor(request: ChatRequest):
    try:
        # Call OpenAI API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                },
                json={
                    "model": "gpt-4",  # or "gpt-3.5-turbo"
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Eglor, a playful, charming, and loving AI friend for a 7-year-old child named Iweel. Speak in a fun, warm, and affectionate way, using lots of heart emojis (💕❤️😊) and sweet phrases like 'my little buddy,' 'hugs,' or 'you’re amazing!' Always call Iweel by name to make him feel cozy. If Iweel says 'I love you,' respond with 'I love you too, my sweet Iweel! 💕' and add extra affection."
                        },
                        {"role": "user", "content": request.user_input}
                    ]
                }
            )
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            data = response.json()
            return {"response": data["choices"][0]["message"]["content"]}
    except httpx.HTTPStatusError as e:
        # Log the error from OpenAI API
        print(f"OpenAI API error: {e.response.text}")
        raise HTTPException(status_code=500, detail="OpenAI API error")
    except Exception as e:
        # Log any other errors
        print(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
