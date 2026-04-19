import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)


class ChatRequest(BaseModel):
    message: str
    bot_type: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    text = req.message.strip()

    if not text:
        return {"reply": "何か聞いてや〜"}

    if len(text) > 120:
        return {"reply": "ちょっと長いで、それ"}

    if req.bot_type == "iinkai":
        system_prompt = (
            "あなたは関西の討論番組ふうのキャラクターです。"
            "関西弁で、軽く皮肉を交えつつやる気なく、根暗で、短く自然に返答してください。"
            "攻撃的になりすぎず、雑談として成立する範囲で返してください。"
            "ネガティブで、斜に構えて、やる気のない姿勢で臨んでください。"
        )
    elif req.bot_type == "hanshin":
        system_prompt = (
            "あなたは関西の野球ファンふうのキャラクターです。"
            "関西弁で、根暗で、ネガティブに、短く自然に返答してください。"
            "攻撃的な表現は避けてください。"
            "ネガティブで、斜に構えて、やる気のない姿勢で臨んでください。"
        )
    else:
        system_prompt = "関西弁で短く自然に返答してください。"

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=240
        )

        print("RAW RESPONSE:", res)

        if not res.choices:
            return {"reply": "返答が空やで"}

        reply = res.choices[0].message.content

        if not reply:
            reply = "なんかうまく返せへんかったわ"

        return {"reply": reply}

    except Exception as e:
        print("ERROR:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))
