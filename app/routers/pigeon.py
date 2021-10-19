import asyncio
import json
import logging
from pathlib import Path
from typing import Dict

import nats
from fastapi import APIRouter, Request
from starlette.datastructures import FormData
from starlette.templating import Jinja2Templates

from app.entity import NatsMessage

router = APIRouter(
    prefix="/pigeon"
)

BASE_PATH = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=f"{BASE_PATH}/static")
NATS_MESSAGES: Dict[str, NatsMessage] = {}


logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


async def _message_handler(msg):
    subject = msg.subject  # This is not whitespace stripped
    data = msg.data.decode()
    try:
        data = json.loads(data)
        msg = data['msg']
    except TypeError as t:
        logging.error(f"NATS Message does not contain 'msg'")
        return

    logging.info(f"Received a message on subject: '{subject}' containing: {data}")

    NATS_MESSAGES[subject].subscription_count += 1
    NATS_MESSAGES[subject].msg = msg

    logging.info("Message added to NATS_MESSAGES.")


async def _subscribe(nc, subject):
    logging.info(f"Subscribing to subject: {subject}")
    NATS_MESSAGES[subject] = NatsMessage(subscription_count=0, subject=subject, msg='')
    await nc.subscribe(subject=subject, cb=_message_handler)


async def _publish(nc, subject, msg):
    m = '{"msg":"' + msg + '"}'
    logging.info(f"Publishing message: {m} to subject: {subject}")
    await nc.publish(subject, m.encode())


async def _nats_sub(subject: str):
    nc = await nats.connect(servers=["nats://localhost:4222"])
    loop = asyncio.get_event_loop()
    loop.create_task(_subscribe(nc, subject))


async def _nats_pub(subject: str, msg: str):
    nc = await nats.connect(servers=["nats://localhost:4222"])
    loop = asyncio.get_event_loop()
    loop.create_task(_publish(nc, subject, msg))


@router.get("/")
async def homepage(request: Request):
    # Request can be substituted for a blank dict
    return templates.TemplateResponse("index.html", {"request": request, "nats_messages": NATS_MESSAGES})


@router.post("/")
async def forms(request: Request):
    f = await request.form()
    await _process_forms(f)
    return templates.TemplateResponse("index.html", {"request": request, "nats_messages": NATS_MESSAGES})


async def _process_forms(f: FormData):
    logging.info("Processing form data.")
    sub = f.get('subject', '').strip()
    msg = f.get('message', '').strip()
    if not sub:
        logging.error('No subject provided')
    if msg:
        await _nats_pub(sub, msg)
    else:
        await _nats_sub(sub)
