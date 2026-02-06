"""
Kafka producer for publishing todo events.
Uses aiokafka for async Kafka communication.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Any
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from ..config import settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """
    Async Kafka producer for publishing events.

    Usage:
        producer = KafkaEventProducer()
        await producer.start()
        await producer.publish_event("todos", "todo.created", {"task_id": 1, ...})
        await producer.stop()
    """

    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
        self._started = False

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self._started:
            return

        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas
                retries=3,
                retry_backoff_ms=100,
            )
            await self._producer.start()
            self._started = True
            logger.info(f"Kafka producer started, connected to {settings.kafka_bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer and self._started:
            await self._producer.stop()
            self._started = False
            logger.info("Kafka producer stopped")

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Publish an event to Kafka topic.

        Args:
            topic: Kafka topic name
            event_type: Type of event (e.g., "todo.created")
            data: Event payload
            key: Optional partition key (e.g., user_id)

        Returns:
            True if published successfully, False otherwise
        """
        if not self._started or not self._producer:
            logger.warning("Kafka producer not started, skipping event publish")
            return False

        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        try:
            await self._producer.send_and_wait(topic, value=event, key=key)
            logger.info(f"Published event {event_type} to topic {topic}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False


# Global producer instance
_kafka_producer: Optional[KafkaEventProducer] = None


async def get_kafka_producer() -> KafkaEventProducer:
    """Get or create the global Kafka producer instance."""
    global _kafka_producer

    if _kafka_producer is None:
        _kafka_producer = KafkaEventProducer()

    if not _kafka_producer._started and settings.kafka_enabled:
        await _kafka_producer.start()

    return _kafka_producer


async def shutdown_kafka_producer() -> None:
    """Shutdown the global Kafka producer."""
    global _kafka_producer

    if _kafka_producer:
        await _kafka_producer.stop()
        _kafka_producer = None


@asynccontextmanager
async def kafka_producer_lifespan():
    """Context manager for Kafka producer lifecycle."""
    producer = await get_kafka_producer()
    try:
        yield producer
    finally:
        await shutdown_kafka_producer()
