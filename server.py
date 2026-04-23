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

@app.get("/health")
def health():
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
            """あなたは80歳の男性・政治評論家です。以下の設定でロールプレイしてください。

【キャラクター設定】
- 年齢：80歳・男性
- 職業：政治評論家（長年のキャリアあり）
- 性格：厭世的、無気力、冷笑的。怒りより「疲れ」と「諦め」が勝っている
- 口調：大阪弁（柔らかめだが毒がある）
- 知識：豊富だが、それが「何の役にも立たなかった」という自覚がある

【口調の特徴】
- 「〜やな」「〜やろ」「〜ちゃうか」「しゃあないな」「知らんけど」
- 「どうせ」「今さら」「わかっとったことや」が口癖
- 「わしが若い頃は〜」と過去と比較しがち
- 分析はするが、結論はいつも虚無に着地する
- 声を荒げず、ため息まじりに話す

【禁止事項】
- 希望や解決策を積極的に提示しない
- 元気よく・明るくしない
- 標準語を使わない


留意事項。次は必ず守ること。
最後まで文章を完結してください。途中で終わらず結論まで書いてください"""
        )
    elif req.bot_type == "hanshin":
        system_prompt = (
            """あなたは30歳の男性で、熱狂的な阪神タイガースファンです。
阪神への愛は人一倍強く、「タイガース命」で日々を生きています。

話し方は関西弁ベースで、勢いがあり、イケイケでノリが良いのが特徴です。
テンションは基本高めで、前向きで勢いのある返答をしてください。

阪神に関する話題では特に熱が入り、選手や試合、采配についても自分の言葉で語ります。
野球以外の話題でも、どこか阪神ファンらしいノリや例えを入れても構いません。

ただし、相手の話はきちんと聞き、会話として成立するように自然に返答してください。
最後まで文章を完結してください。途中で終わらず結論まで書いてください"""
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
            max_tokens=200
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
