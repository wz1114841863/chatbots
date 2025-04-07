import os

from typing import Sequence
from typing_extensions import Annotated, TypedDict
from API_KEY import DEEPSEEK_API, LANGSMITH_API_KEY
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.messages import SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.message import add_messages


BASE_URL = "https://api.deepseek.com"
API_KEY = DEEPSEEK_API

MODEL_NAMES = [
    "deepseek-chat",  # DeepSeek-V3
    "deepseek-reasoner",  # DeepSeek-R1
]

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY

model = ChatOpenAI(
    model=MODEL_NAMES[0],
    base_url=BASE_URL,
    api_key=API_KEY,
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

trimmer = trim_messages(
    max_tokens=100,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str


def call_model(state: State):
    # deepseek api 如何获得token数量来进行裁剪呢.
    # trimmed_messages = trimmer.invoke(state["messages"])
    # prompt = prompt_template.invoke(
    #     {"messages": trimmed_messages, "language": state["language"]}
    # )
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}


workflow = StateGraph(state_schema=State)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


if __name__ == "__main__":
    # config = {"configurable": {"thread_id": "abc123"}}
    # query = "Hello! I am wz."
    # language = "chinese"
    # input_messages = [HumanMessage(query)]
    # output = app.invoke({"messages": input_messages, "language": language}, config)
    # output["messages"][-1].pretty_print()

    # query = "What's my name?"
    # input_messages = [HumanMessage(query)]
    # output = app.invoke({"messages": input_messages, "language": language}, config)
    # output["messages"][-1].pretty_print()

    # config_1 = {"configurable": {"thread_id": "abc234"}}
    # query = "What's my name?"
    # input_messages = [HumanMessage(query)]
    # output = app.invoke({"messages": input_messages, "language": language}, config_1)
    # output["messages"][-1].pretty_print()

    # query = "Are you remember my name?"
    # input_messages = [HumanMessage(query)]
    # output = app.invoke({"messages": input_messages, "language": language}, config)
    # output["messages"][-1].pretty_print()

    # 试验stream
    config_2 = {"configurable": {"thread_id": "abc789"}}
    query = "你好, 我该如何使用deepseek api 来获取一段输入的token数, 我使用trim_messages时报错, 报错信息为'NotImplementedError: get_num_tokens_from_messages() is not presently implemented for model cl100k_base', 我该如何解决."
    language = "chinese"
    input_messages = [HumanMessage(query)]
    for chunk, metadata in app.stream(
        {"messages": input_messages, "language": language},
        config_2,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage):  # Filter to just model responses
            print(chunk.content, end="|")
