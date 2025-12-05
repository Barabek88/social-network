import json
from app.core.rabbitmq_client import rabbitmq_client
from app.core.websocket_manager import ws_manager
from app.logger import logger
from uuid import UUID
import aio_pika


async def process_feed_message(message: aio_pika.IncomingMessage):
    async with message.process():
        post_data = json.loads(message.body.decode())
        user_id = UUID(message.routing_key.split(".")[-1])

        logger.info(f"Processing feed update for user {user_id}")
        await ws_manager.send_post_to_user(user_id, post_data)


async def start_feed_worker():
    await rabbitmq_client.connect()

    channel = await rabbitmq_client.connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        "post_feed", aio_pika.ExchangeType.TOPIC, durable=True
    )

    queue = await channel.declare_queue("feed_updates", durable=True)
    await queue.bind(exchange, routing_key="user.*")

    await queue.consume(process_feed_message)
    logger.info("Feed worker started")
