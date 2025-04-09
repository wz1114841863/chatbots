import streamlit as st
import requests
import sqlite3

FASTAPI_URL = "http://localhost:8000"

# 初始化Session状态
if "current_convo" not in st.session_state:
    st.session_state.current_convo = None
if "messages" not in st.session_state:
    st.session_state.messages = []


# 获取对话列表
def get_conversations():
    response = requests.get(f"{FASTAPI_URL}/conversations")
    return response.json() if response.ok else []


# 创建新对话
def create_convo():
    response = requests.post(f"{FASTAPI_URL}/conversations/new")
    if response.ok:
        convo_id = response.json()["convo_id"]
        st.session_state.current_convo = convo_id
        st.session_state.messages = []


# 加载对话
def load_conversation(convo_id):
    response = requests.get(f"{FASTAPI_URL}/conversations/{convo_id}")
    if response.ok:
        data = response.json()
        st.session_state.current_convo = convo_id
        st.session_state.messages = data["message"]


# 侧边栏 - 对话管理
with st.sidebar:
    st.header("对话管理")

    st.subheader("新建对话")
    if st.button("+ 开始新对话", use_container_width=True):
        create_convo()

    st.subheader("最近对话")
    conversations = get_conversations()
    for convo in conversations:
        btn = st.button(
            f"💬 {convo['title']}",
            key=convo["id"],
            use_container_width=True,
        )
        if btn:
            load_conversation(convo["id"])

# 主界面 - 聊天窗口
st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by DeepSeek API.")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("请输入您的问题..."):
    # 显示用户消息
    st.chat_message("user").write(prompt)

    # 发送到后端
    response = requests.post(
        f"{FASTAPI_URL}/conversations/send",
        json={
            "conv_id": st.session_state.current_convo,
            "content": prompt,
        },
    )
    if response.ok:
        ai_msg = response.json()["response"]
        st.chat_message("assistant").write(ai_msg)
        st.session_state.messages.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": ai_msg},
            ]
        )
    else:
        st.error("消息发送失败,请重试")
