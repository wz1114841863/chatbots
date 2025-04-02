import openai
import requests
import json

from API_KEY import DEEPSEEK_API

BASE_URL = "https://api.deepseek.com"
API_KEY = DEEPSEEK_API

MODEL_NAMES = [
    "deepseek-chat",  # DeepSeek-V3
    "deepseek-reasoner",  # DeepSeek-R1
]

TEMPERATURE = [
    0.0,  # 代码生成, 数学解题
    1.0,  # 数据抽取, 数据分析
    1.3,  # 通用对话
    1.5,  # 创意类写作, 诗歌创作
]

ERR_CODE = {
    400: "请求体格式错误",
    401: "API Key 错误, 认证失败",
    402: "账户余额不足",
    422: "请求体参数错误",
    429: "请求速率达到上限",
    500: "服务器内部故障",
    503: "服务器负载过高",
}


def completions_api():
    """通过OpenAI接口测试API KEY"""
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )
    response = client.chat.completions.create(
        model=MODEL_NAMES[0],
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        max_tokens=1024,
        temperature=TEMPERATURE[2],
        stream=False,  # 是否流式输出
    )

    print(response.choices[0].message.content)


def fim_beta_api():
    """测试FIM补全"""
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL + "/beta",
    )
    response = client.completions.create(
        model=MODEL_NAMES[0],
        prompt="def fib(a):",
        suffix="    return fib(a-1) + fib(a-2)",
        max_tokens=128,
    )
    print(response.choices[0].text)


def list_model_api():
    """列出可用模型"""
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )
    print(client.models.list())


def request_completions():
    """通过request请求测试, 对话补全
    请求体格式和响应体内容参考:
    https://api-docs.deepseek.com/zh-cn/api/create-chat-completion
    """
    url = BASE_URL + "/chat/completions"

    payload = json.dumps(
        {
            "messages": [
                {
                    "content": "You are a helpful assisant.",
                    "role": "system",
                },
                {
                    "content": "Hi",
                    "role": "user",
                },
            ],
            "model": MODEL_NAMES[0],
            "frequency_penalty": 0,
            "max_tokens": 2048,
            "presence_penalty": 0,
            "response_format": {
                "type": "text",
            },
            "stop": None,
            "stream": False,
            "stream_options": None,
            "temperature": TEMPERATURE[2],
            "top_p": 1,
            "tools": None,
            "tool_choice": "none",
            "logprobs": False,
            "top_logprobs": None,
        }
    )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def request_fim_beta():
    """通过request请求测试, FIM补全
    请求体格式和响应体内容参考:
    https://api-docs.deepseek.com/zh-cn/api/create-chat-completion
    """
    url = BASE_URL + "/beta/completions"

    payload = json.dumps(
        {
            "model": MODEL_NAMES[0],
            "prompt": "def fib(a):",
            "echo": False,
            "frequency_penalty": 0,
            "logprobs": 0,
            "max_tokens": 1024,
            "presence_penalty": 0,
            "stop": None,
            "stream": False,
            "stream_options": None,
            "suffix": "    return fib(a-1) + fib(a-2)",
            "temperature": 1,
            "top_p": 1,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def request_list_model():
    """通过request请求测试, 获取模型列表"""
    url = BASE_URL + "/models"
    payload = {}
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)


def request_query_balance():
    """通过request请求测试, 查询余额"""
    url = BASE_URL + "/user/balance"
    payload = {}
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)


def resoner_api():
    """针对推理模型deepseek-reasoner
    输入参数
    1. max_tokens: 不含思维链输出长度
    2. reasoning_effort: 控制思维链的长度
    输出参数:
    1. resoning_content: 思维链内容
    2. content: 最终回答内容
    仅支持对话补全和对话前缀续写, 不支持调节参数(temperature, top_p等)

    上下文拼接过程中, 思维链路内容不会拼接
    """
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )
    messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
    response = client.chat.completions.create(
        model=MODEL_NAMES[1],  # 推理模型
        messages=messages,
        max_tokens=1024,
        stream=False,  # 是否流式输出
    )
    reasoning_content = response.choices[0].message.reasoning_content
    content = response.choices[0].message.content
    print(f"reasoning_content: {reasoning_content}")
    print(f"content: {content}")

    messages.append({"role": "assistant", "content": content})  # 上下文
    messages.append(
        {"role": "user", "content": "How many Rs are there in the word 'strawberry'?"}
    )
    response = client.chat.completions.create(
        model=MODEL_NAMES[1],  # 推理模型
        messages=messages,
        max_tokens=1024,
        stream=False,  # 是否流式输出
    )
    reasoning_content = response.choices[0].message.reasoning_content
    content = response.choices[0].message.content
    print(f"reasoning_content: {reasoning_content}")
    print(f"content: {content}")


def resoner_stream_api():
    """针对推理模型deepseek-reasoner, 采用流式传输"""
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )
    messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
    response = client.chat.completions.create(
        model=MODEL_NAMES[1],  # 推理模型
        messages=messages,
        max_tokens=1024,
        stream=True,  # 是否流式输出
    )
    reasoning_content = ""
    content = ""
    for chunk in response:
        if (
            hasattr(chunk.choices[0].delta, "reasoning_content")
            and chunk.choices[0].delta.reasoning_content
        ):
            reasoning_content += chunk.choices[0].delta.reasoning_content
        if (
            hasattr(chunk.choices[0].delta, "content")
            and chunk.choices[0].delta.content
        ):
            content += chunk.choices[0].delta.content
    print(f"reasoning_content: {reasoning_content}")
    print(f"content: {content}")

    messages.append({"role": "assistant", "content": content})  # 上下文
    messages.append(
        {"role": "user", "content": "How many Rs are there in the word 'strawberry'?"}
    )
    response = client.chat.completions.create(
        model=MODEL_NAMES[1],  # 推理模型
        messages=messages,
        max_tokens=1024,
        stream=True,  # 是否流式输出
    )
    reasoning_content = ""
    content = ""
    for chunk in response:
        if (
            hasattr(chunk.choices[0].delta, "reasoning_content")
            and chunk.choices[0].delta.reasoning_content
        ):
            reasoning_content += chunk.choices[0].delta.reasoning_content
        if (
            hasattr(chunk.choices[0].delta, "content")
            and chunk.choices[0].delta.content
        ):
            content += chunk.choices[0].delta.content
    print(f"reasoning_content: {reasoning_content}")
    print(f"content: {content}")


def many_rounds_dialogue():
    """多轮对话"""
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )
    messages = [
        {
            "role": "user",
            "content": "What's the highest mountain in the world? tell me answer only.",
        }
    ]
    response = client.chat.completions.create(
        model=MODEL_NAMES[0],
        messages=messages,
        max_tokens=1024,
        stream=False,
    )
    role = response.choices[0].message.role
    content = response.choices[0].message.content
    messages.append({"role": role, "content": content})
    print(f"Messages Round 1: {messages}")

    messages.append({"role": "user", "content": "What is the second?"})
    response = client.chat.completions.create(
        model=MODEL_NAMES[0],
        messages=messages,
        max_tokens=1024,
        stream=False,
    )
    role = response.choices[0].message.role
    content = response.choices[0].message.content
    messages.append({"role": role, "content": content})
    print(f"Messages Round 1: {messages}")


def dialog_prefix_beta():
    """对话前缀续写
    用户提供assistant开头的消息, 让模型补全其余的消息
    使用对话前缀续写时, 用户需确保 messages 列表里最后一条消息的 role 为 assistant,
    并设置最后一条消息的 prefix 参数为 True.
    """
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL + "/beta",
    )
    messages = [
        {"role": "user", "content": "Please write quick sort code"},
        {"role": "assistant", "content": "```python\n", "prefix": True},
    ]
    response = client.chat.completions.create(
        model=MODEL_NAMES[0],
        messages=messages,
        stop=["```"],  # 避免模型额外解释
    )
    print(response.choices[0].message.content)


def json_output_api():
    """让模型严格按照json格式输出
    1. 设置response_format格式: {"type": "json_object"}
    2. 用户传入的 system 或 user prompt 中必须含有 json 字样,
    并给出希望模型输出的 JSON 格式的样例,以指导模型来输出合法 JSON.
    3. 需要合理设置max_tokens参数, 防止JSON字符串被截断.
    """
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    system_prompt = """
        The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format.

        EXAMPLE INPUT:
        Which is the highest mountain in the world? Mount Everest.

        EXAMPLE JSON OUTPUT:
        {
            "question": "Which is the highest mountain in the world?",
            "answer": "Mount Everest"
        }
    """
    user_prompt = "Which is the longest river in the world? The Nile River."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = client.chat.completions.create(
        model=MODEL_NAMES[0],
        messages=messages,
        response_format={
            "type": "json_object",
        },
    )
    print(json.loads(response.choices[0].message.content))


def function_calling():
    """让模型能够调用外部工具, 来增强自身能力."""

    def get_weather(location):
        return "24°C"

    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    messages = [{"role": "user", "content": "How's the weather in Hangzhou?"}]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather of an location, the user shoud supply a location first",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model=MODEL_NAMES[0],
        messages=messages,
        tools=tools,
    )

    # 检查是否有 tool_calls
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        tool_id = tool_call.id
        function_name = tool_call.function.name
        function_args = tool_call.function.arguments

        print(f"Tool ID: {tool_id}")
        print(f"Function Name: {function_name}")
        print(f"Function Arguments: {function_args}")

        # 需要添加tool_calls对应tool_call_id， 否则报错
        assistant_message = response.choices[0].message
        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls,
            }
        )

        # 调用本地函数
        if function_name == "get_weather":
            location = eval(function_args)["location"]  # 解析参数
            weather_result = get_weather(location)

            # 添加 tool 消息
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "name": function_name,
                    "content": weather_result,
                }
            )

            # 第二次请求，获取最终响应
            response = client.chat.completions.create(
                model=MODEL_NAMES[0],
                messages=messages,
                tools=tools,
            )
            print(f"Final Response: {response.choices[0].message.content}")
        else:
            print("Unknown function called.")
    else:
        print("No tool calls triggered.")


if __name__ == "__main__":
    function_calling()
