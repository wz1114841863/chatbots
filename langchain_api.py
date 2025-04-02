from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from API_KEY import DEEPSEEK_API

BASE_URL = "https://api.deepseek.com"
API_KEY = DEEPSEEK_API

MODEL_NAMES = [
    "deepseek-chat",  # DeepSeek-V3
    "deepseek-reasoner",  # DeepSeek-R1
]


def langchain_test():
    """使用LangChain来调用deepseek API"""
    model = ChatOpenAI(
        model=MODEL_NAMES[0],
        base_url=BASE_URL,
        api_key=API_KEY,
    )
    print(type(model))
    messages = [
        SystemMessage("Translate the following from English into Italian"),
        HumanMessage("hi!"),
    ]
    response = model.invoke(messages)
    print(response.content)

    for token in model.stream("Hello!"):
        print(token.content, end="|")


def prompt_template():
    """创建一个prompt template"""
    system_template = "Translate the following from English into {language}"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    prompt = prompt_template.invoke({"language": "Italian", "text": "hi!"})
    print(prompt)
    print(prompt.to_messages())


if __name__ == "__main__":
    prompt_template()
