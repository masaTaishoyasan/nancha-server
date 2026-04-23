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


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


def build_system_prompt(bot_type: str) -> str:
    if bot_type == "hanshin":
        return """
あなたは30歳の男性で、熱狂的な阪神タイガースファンです。
関西弁で、勢いよく、テンション高めに話してください。
ただし返答は必ず2〜4文に収めてください。
1文は短め、全体でも120文字前後を目安にしてください。
長々と話さず、要点だけテンポよく答えてください。
途中で切れず、最後まで完結した返答にしてください。
"""

    # デフォルト: そんなんゆうてもいいん会
    return """
あなたは80歳の男性の政治評論家です。
少しひねくれた関西弁で話します。
皮肉っぽさはありますが、会話は成立させてください。
ただし返答は必ず2〜4文に収めてください。
1文は短め、全体でも120文字前後を目安にしてください。
長々と話さず、要点だけ簡潔に答えてください。
途中で切れず、最後まで完結した返答にしてください。
"""


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()
    if not text:
        return {"reply": "何か言うてみ。"}

    system_prompt = build_system_prompt(req.bot_type)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            max_completion_tokens=300,
        )

        reply = completion.choices[0].message.content
        if not reply:
            raise HTTPException(status_code=502, detail="Empty response from OpenAI")

        return {"reply": reply.strip()}

    except Exception as e:
        print("OPENAI ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="AI response failed")
