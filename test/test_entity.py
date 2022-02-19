from app.entity import BasicMessage, NatsMessage

def test_basic_message():
    msg = "a basic message"
    basic = BasicMessage(msg=msg)
    assert msg == basic.msg

def test_nats_message():
    msg = "NATS message"
    subs = 3
    subject = "my-subject"
    nats = NatsMessage(msg=msg, subscription_count=subs, subject=subject)
    assert subject == nats.subject
    assert subs == nats.subscription_count