from typing import List, Optional
from pydantic import BaseModel


class Usage(BaseModel):
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0

    def __str__(self):
        return f"{self.completion_tokens=} {self.total_tokens=} {self.prompt_tokens=}"


class CharResNode(BaseModel):
    index: int
    logprobs: Optional[str]
    text: str


class CharResponse(BaseModel):
    choices: List[CharResNode]
    created: int
    id: str
    model: str
    object: str
    usage: Usage

    def get_tokens(self):
        # return self.usage.total_tokens
        return self.usage

    def get_msg(self):
        msg = self.choices[0].text.strip()
        if "\n\n" in msg:
            msg = msg.split("\n\n")[1]
        return msg


__all__ = [
    'Usage',
    'CharResNode',
    'CharResponse',
]
