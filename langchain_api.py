from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
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


def document_load():
    """加载文件, 生成document对象"""
    file_path = "./tmp/nke-10k-2023.pdf"
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(len(docs))
    # print(f"{docs[0].page_content[:200]}\n")
    # print(docs[0].metadata)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    all_splits = text_splitter.split_documents(docs)
    print(len(all_splits))

    # 如何获取deepseek embedding模型.
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=API_KEY)
    # vector_1 = embeddings.embed_query(all_splits[0].page_content)
    # vector_2 = embeddings.embed_query(all_splits[1].page_content)
    # assert len(vector_1) == len(vector_2)
    # print(f"Generated vectros of length {len(vector_1)}")
    # print(vector_1[0])


if __name__ == "__main__":
    document_load()
