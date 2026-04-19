import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    bot_type: str

@app.post("/chat")
def chat(req: ChatRequest):
    text = req.message.strip()

    if not text:
        return {"reply": "何か聞いてや〜"}

    if len(text) > 120:
        return {"reply": "ちょっと長いで、それ"}

    if req.bot_type == "iinkai":
        system_prompt = "関西の討論番組風に、軽く皮肉を交えて短く答えてください。"
    else:
        system_prompt = "関西の野球ファン風に、楽しく短く答えてください。"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        max_tokens=120
    )

    reply = res.choices[0].message.content
    return {"reply": reply}
