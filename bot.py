from dotenv import load_dotenv
import os
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

from scrap_billboard import add_hot100_in_spotify_playlists

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route('/')
def hello():
    name = "Hello world"
    return name

@app.route("/callback", methods=["POST"])
def callback():
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)
        return "OK"

# 請輸入日期
@handler.add(MessageEvent, message=TextMessage)
def add_spotify_playlist(event):
    result_url = add_hot100_in_spotify_playlists(event.message.text)
    if result_url is None:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"該日無資料，請重新輸入日期。")

        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"已經成功新增{event.message.text} 這個禮拜的 Billboard Hot 100 進 Spotify。")
        )

# if __name__ == "__main__":
#     app.run()