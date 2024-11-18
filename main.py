import asyncio
from typing import Any, Callable
import betterproto
from douyinlivewebfetcher.liveMan import DouyinLiveWebFetcher
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from douyinlivewebfetcher.protobuf.douyin import (
    ChatMessage,
    GiftMessage,
    LikeMessage,
    MemberMessage,
    SocialMessage,
)
import janus


class MyDouyinLiveWebFetcher(DouyinLiveWebFetcher):
    def __init__(self, live_id, on_msg: Callable[[betterproto.Message], Any] | None = None):
        self.on_msg = on_msg
        super().__init__(live_id)

    def _parseChatMsg(self, payload: bytes):
        """聊天消息"""
        message = ChatMessage().parse(payload)
        if self.on_msg:
            try:
                self.on_msg(message)
            except Exception:
                pass

    def _parseGiftMsg(self, payload: bytes):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        if self.on_msg:
            try:
                self.on_msg(message)
            except Exception:
                pass

    def _parseLikeMsg(self, payload: bytes):
        """点赞消息"""
        message = LikeMessage().parse(payload)
        if self.on_msg:
            try:
                self.on_msg(message)
            except Exception:
                pass

    def _parseMemberMsg(self, payload: bytes):
        """进入直播间消息"""
        message = MemberMessage().parse(payload)
        if self.on_msg:
            try:
                self.on_msg(message)
            except Exception:
                pass

    def _parseSocialMsg(self, payload: bytes):
        """关注消息"""
        message = SocialMessage().parse(payload)
        if self.on_msg:
            try:
                self.on_msg(message)
            except Exception:
                pass
    def _parseRoomUserSeqMsg(self, payload: bytes):
        """直播间统计"""
        return
        # message = RoomUserSeqMessage().parse(payload)

    def _parseFansclubMsg(self, payload: bytes):
        """粉丝团消息"""
        return
        # message = FansclubMessage().parse(payload)

    def _parseControlMsg(self, payload: bytes):
        """直播间状态消息"""
        return
        # message = EmojiChatMessage().parse(payload)

    def _parseEmojiChatMsg(self, payload: bytes):
        """聊天表情包消息"""
        return
        # message = RoomMessage().parse(payload)

    def _parseRoomStatsMsg(self, payload: bytes):
        """直播间统计信息"""
        return
        # message = RoomStatsMessage().parse(payload)

    def _parseRoomMsg(self, payload: bytes):
        """直播间信息"""
        return
        # message = RoomRankMessage().parse(payload)

    def _parseRankMsg(self, payload: bytes):
        """直播间排行榜信息"""
        return
        # message = ControlMessage().parse(payload)


app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data) 
                console.log(data?.common?.method, data);
            };
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


# if __name__ == "__main__":
#     live_id = "6096197105"

#     def on_chat_msg(msg: ChatMessage):
#         print(msg.content)

#     MyDouyinLiveWebFetcher(live_id, on_chat_msg=on_chat_msg).start()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    live_id = "525960662143"
    queue: janus.Queue[betterproto.Message] = janus.Queue()

    async def pong():
        while True:
            msg = await queue.async_q.get()
            await websocket.send_text(msg.to_json())

    def on_msg(msg: betterproto.Message):
        queue.sync_q.put(msg)

    douyin_fetcher = MyDouyinLiveWebFetcher(live_id, on_msg=on_msg)

    try:
        douyin_fetcher_coro = asyncio.to_thread(douyin_fetcher.start)
        await asyncio.gather(pong(), douyin_fetcher_coro)
    except Exception:
        pass

    douyin_fetcher.stop()
