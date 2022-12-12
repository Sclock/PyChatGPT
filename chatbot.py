import json
import uuid
import time
import asyncio
import aiohttp
from aiohttp import TCPConnector
from pydantic import BaseModel
from typing import AsyncGenerator, Optional


USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
)


# The request interval in seconds.
REQUEST_DURATION = 5


class ChatbotContext(BaseModel):
    """
    It makes the contexts independent for different people or groups.
    """

    conversation_id: Optional[str] = None
    parent_id: str = ''

    config_name: str = "config"
    json_value: dict = {}

    def reset(self):
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

        self.json_value["conversation_id"] = None
        self.json_value["parent_id"] = self.parent_id
        self.save()

    @classmethod
    def load(cls):
        with open("config", "r", encoding="utf-8") as f:
            json_value: dict = json.load(f)
        if json_value:
            self = ChatbotContext.parse_obj(json_value)
            self.json_value = json_value
            return self

    def save(self):
        with open(self.config_name, "w", encoding="utf-8") as f:
            json.dump(
                self.json_value, f,
                ensure_ascii=False, indent=4
            )

    def set_conversation_id(self, conversation_id):
        if conversation_id != self.conversation_id:
            self.conversation_id = conversation_id
            self.json_value["conversation_id"] = conversation_id
            print("更新conversation_id")
            self.save()

    def set_parent_id(self, parent_id):
        if parent_id != self.parent_id:
            self.parent_id = parent_id
            self.json_value["parent_id"] = parent_id
            # print("更新parent_id")
            self.save()


class Chatbot:
    """
    The chatbot to interact with ChatGPT.
    You should use `Chatbot.get_instance` to get the ›chatbot object,
    as it will refresh the session token by default.
    >>> await Chatbot.get_instance()
    """

    _instance: Optional['Chatbot'] = None

    def __init__(self):
        self._authorization = "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"
        with open("session_token", "r", encoding="utf-8") as f:
            self._session_token = f.readline()
        self._last_request_time = 0
        self._contexts: ChatbotContext = ChatbotContext.load()

    async def _sleep_for_next_request(self):
        now = int(time.time())
        request_should_after = self._last_request_time + REQUEST_DURATION
        if request_should_after > now:
            # Sleep the remaining seconds.
            await asyncio.sleep(request_should_after - now)
        self._last_request_time = int(time.time())

    @classmethod
    async def get_instance(cls) -> 'Chatbot':
        """
        # 获取唯一链接实例
        """

        if cls._instance is not None:
            return cls._instance

        cls._instance = Chatbot()
        await cls._instance.refresh_session()
        return cls._instance

    def reset_or_create_context(self):
        """
        重设context
        """

        self._contexts.reset()

    def get_or_create_context(self) -> ChatbotContext:
        """
        获取当前context
        """
        return self._contexts

    @property
    def _headers(self) -> dict[str, str]:
        return {
            'Accept': 'application/json',
            'Authorization': self._authorization,
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
        }

    async def get_chat_lines(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        获取回复
        """
        cached_line = ''
        skip = 0
        async for line in self._get_chat_stream(prompt):
            cached_line = line[skip:]
            if cached_line.endswith('\n'):
                skip += len(cached_line)
                yield cached_line.strip()

        if cached_line != '':
            yield cached_line.strip()

    async def _get_chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        ctx = self.get_or_create_context()
        data = json.dumps({
            'action': 'next',
            'messages': [
                {
                    'id': str(uuid.uuid4()),
                    'role': 'user',
                    'content': {
                        'content_type': 'text',
                        'parts': [prompt]
                    }
                }
            ],
            'conversation_id': ctx.conversation_id,
            'parent_message_id': ctx.parent_id,
            'model': 'text-davinci-002-render'
        })

        await self._sleep_for_next_request()

        async with aiohttp.ClientSession(
            raise_for_status=True,
            headers=self._headers,
            # connector=ProxyConnector.from_url('socks5://127.0.0.1:33211')
            connector=TCPConnector(ssl=False),
        ) as client:
            async with client.post(
                'https://chat.openai.com/backend-api/conversation',
                data=data,

            ) as resp:
                async for line in resp.content:
                    try:
                        line = json.loads(line.decode('utf-8')[6:])
                        message = line['message']['content']['parts'][0]
                        ctx.set_conversation_id(line['conversation_id'])
                        ctx.set_parent_id(line['message']['id'])
                        yield message
                    except (IndexError, json.decoder.JSONDecodeError):
                        continue

    async def refresh_session(self):
        """
        刷新令牌
        """

        cookies = {
            '__Secure-next-auth.session-token': self._session_token
        }

        await self._sleep_for_next_request()

        async with aiohttp.ClientSession(
            cookies=cookies,
            headers=self._headers,
            # connector=ProxyConnector.from_url('socks5://127.0.0.1:33211')
            connector=TCPConnector(ssl=False),
        ) as client:
            async with client.get(
                'https://chat.openai.com/api/auth/session',
                # connector=ProxyConnector.from_url('socks5://127.0.0.1:33211')
            ) as resp:
                self._session_token = resp.cookies.get(
                    '__Secure-next-auth.session-token')
                self._authorization = (await resp.json())['accessToken']
                with open("session_token", "w", encoding="utf-8") as f:
                    f.write(self._session_token.value)
                print("session_token更新")
