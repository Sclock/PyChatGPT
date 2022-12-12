import asyncio

import aiohttp

from chatbot import Chatbot


async def start():
    cb = await Chatbot.get_instance()

    while True:
        msg = input("你: \n")
        print()

        if msg == "重置":
            # 重置
            cb.reset_or_create_context()
            print("已清除AI记录\n")
        elif msg == "刷新":
            # 刷新session
            await cb.refresh_session()
            print("已刷新登录信息\n")
        elif msg == "退出":
            break
        else:
            # 发送信息
            print("AI:")
            try:
                async for line in cb.get_chat_lines(msg):
                    print(line)
            except (aiohttp.ClientResponseError, aiohttp.client_exceptions.ServerDisconnectedError) as e:
                print("发生错误", e)
            print()

asyncio.run(start())
