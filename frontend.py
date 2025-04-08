import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000"

# 初始化Session状态
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_convo" not in st.session_state:
    st.session_state.current_convo = None


# 创建新对话
def create_convo():
    response = requests.post(f"{FASTAPI_URL}/conversations/")
    if response.ok:
        convo_id = response.json()["conversation_id"]
        st.session_state.conversations.append(convo_id)
        st.session_state.current_convo = convo_id


# 侧边栏 - 对话管理
with st.sidebar:
    st.header("对话管理")
    if st.button("新建对话"):
        create_convo()
    st.write("---")
    for convo_id in st.session_state.conversations:
        if st.button(f"对话:{convo_id[:8]}", key=convo_id):
            st.session_state.current_convo = convo_id

# 主界面 - 聊天窗口
st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by DeepSeek API.")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
