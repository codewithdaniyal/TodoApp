"""
Kafka event handling for Todo application.
Phase V: Event-driven architecture with Kafka.
"""

from .kafka_producer import KafkaEventProducer, get_kafka_producer

__all__ = ["KafkaEventProducer", "get_kafka_producer"]
