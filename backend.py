import uuid
import sqlite3

from pydantic import BaseModel
from interface import app as chat_app
from fastapi import FastAPI, HTTPException

from langchain_core.messages import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_community.llms import OpenAI

app = FastAPI()


class MessageRequest(BaseModel):
    convo_id: str
    content: str


# 创建新对话
@app.post("/conversations/new")
def create_conversation():
    convo_id = str(uuid.uuid4())
    with sqlite3.connect("./database/chat.db") as conn:
        conn.execute(
            "INSERT INTO conversations (id, title) VALUES (?, ?)", (convo_id, "新对话")
        )
    return {"convo_id": convo_id}


# 发送消息
@app.post("/conversations/send")
def send_message(request: MessageRequest):
    # 保存用户消息
    with sqlite3.connect("chat.db") as conn:
        # 检查对话是否存在
        cur = conn.execute(
            "SELECT 1 FROM conversations WHERE id=?", (request.convo_id,)
        )
        if not cur.fetchone():
            raise HTTPException(404, "对话不存在")

        # 保存用户消息
        conn.execute(
            """
            INSERT INTO messages (convo_id, role, content)
            VALUES (?, 'user', ?)
        """,
            (request.convo_id, request.content),
        )

        # 调用deepseek api接口
        config = {"configurable": {"thread_id": request.convo_id}}
        query = request.content
        language = "chinese"
        input_messages = [HumanMessage(query)]
        output = app.invoke({"messages": input_messages, "language": language}, config)
        ai_response = output["messages"][-1]

        # 保存AI回复
        conn.execute(
            """
            INSERT INTO messages (convo_id, role, content)
            VALUES (?, 'assistant', ?)
        """,
            (request.convo_id, ai_response),
        )

    return {"response": ai_response}


# 获取对话列表
@app.get("/conversations")
def get_conversations(limit: int = 10):
    with sqlite3.connect("chat.db") as conn:
        cur = conn.execute(
            """
            SELECT c.id, c.title, MAX(m.timestamp)
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.convo_id
            GROUP BY c.id
            ORDER BY MAX(m.timestamp) DESC
            LIMIT ?
        """,
            (limit,),
        )
        return [{"id": row[0], "title": row[1]} for row in cur.fetchall()]


# 获取对话详情
@app.get("/conversations/{convo_id}")
def get_conversation(convo_id: str):
    with sqlite3.connect("chat.db") as conn:
        # 获取对话基本信息
        convo = conn.execute(
            "SELECT * FROM conversations WHERE id=?", (convo_id,)
        ).fetchone()
        if not convo:
            raise HTTPException(404, "对话不存在")

        # 获取消息记录
        messages = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE convo_id=?
            ORDER BY timestamp
        """,
            (convo_id,),
        ).fetchall()

    return {
        "id": convo[0],
        "title": convo[1],
        "messages": [{"role": msg[0], "content": msg[1]} for msg in messages],
    }
