import os

from API_KEY import DEEPSEEK_API, LANGSMITH_API_KEY
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph


BASE_URL = "https://api.deepseek.com"
API_KEY = DEEPSEEK_API

MODEL_NAMES = [
    "deepseek-chat",  # DeepSeek-V3
    "deepseek-reasoner",  # DeepSeek-R1
]

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY


def call_model(state: MessagesState):
    response = model.ainvoke(state["messages"])
    return {"messages": response}


model = ChatOpenAI(
    model=MODEL_NAMES[0],
    base_url=BASE_URL,
    api_key=API_KEY,
)
workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "abc123"}}
    query = "Hello! I am wz."
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    output["messages"][-1].pretty_print()

    query = "What's my name?"
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    output["messages"][-1].pretty_print()

    config_1 = {"configurable": {"thread_id": "abc234"}}
    query = "What's my name?"
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config_1)
    output["messages"][-1].pretty_print()

    query = "What's my name?"
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    output["messages"][-1].pretty_print()
