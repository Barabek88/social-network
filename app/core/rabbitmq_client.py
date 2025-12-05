import aio_pika
from app.settings import settings
from app.logger import logger
import json


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        if self.connection is not None:
            logger.info("RabbitMQ already connected")
            return
        
        self.connection = await aio_pika.connect_robust(
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "post_feed", aio_pika.ExchangeType.TOPIC, durable=True
        )
        logger.info("RabbitMQ connected")

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")

    async def publish_post_event(self, user_id: str, post_data: dict):
        if not self.channel:
            raise RuntimeError("RabbitMQ not connected")
        
        message = aio_pika.Message(
            body=json.dumps(post_data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        
        await self.exchange.publish(message, routing_key=f"user.{user_id}")


rabbitmq_client = RabbitMQClient()
