import openai
from Chat import CharResponse


start_sequence = "\nA:\n"
restart_sequence = "Q:\n"
openai.api_key = "这里写你自己的Key"


prompt = ""


while True:
    send_msg = input(restart_sequence)

    # 输入exit退出
    if send_msg == "exit":
        break

    prompt += send_msg

    # 提问
    raw = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        echo=False,
        temperature=1,
        max_tokens=2000,
        frequency_penalty=0,
        presence_penalty=0
    )
    response = CharResponse.parse_obj(raw)

    # 提取消息
    result_msg: str = response.get_msg()

    token = response.get_tokens()
    if token.total_tokens <= 1500 and token.prompt_tokens <= 1500:
        # 添加到上下文
        prompt += "\n" + result_msg

    # # 打印
    print("\n已用内容：", response.get_tokens())
    print("\n消息内容：", result_msg)
