from pydantic import BaseModel


class BasicMessage(BaseModel):
    msg: str


class NatsMessage(BasicMessage):
    subscription_count: int
    subject: str
