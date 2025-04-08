import uuid
import sqlite3

from interface import app as chat_app
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_community.llms import OpenAI

app = FastAPI()


class MessageRequest(BaseModel):
    message: str


@app.post("/conversations/")
def create_conversation():
    """创建一个新的对话"""
    conversation_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": conversation_id}}
    return config


@app.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: str, request: MessageRequest):
    if conversation_id not in conversations:
        raise HTTPException(404, "对话不存在")

    chain = conversations[conversation_id]["chain"]
    # 调用模型生成回复
    response = chain.run(request.message)
    # 记录上下文(LangChain的memory已自动处理)
    conversations[conversation_id]["history"].extend(
        [
            {"type": "human", "content": request.message},
            {"type": "ai", "content": response},
        ]
    )
    return {"response": response}


@app.get("/conversations/{conversation_id}/history")
def get_history(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(404, "对话不存在")
    return conversations[conversation_id]["history"]
