# Please complete the TODO items in the code

from dataclasses import dataclass, field
import json
import random
from datetime import datetime
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from faker import Faker


faker = Faker()

BROKER_URL = "PLAINTEXT://localhost:9092"
TOPIC_NAME = "org.udacity.exercise4.purchases"


def produce(topic_name):
    """Produces data synchronously into the Kafka Topic"""
    #
    # TODO: Configure the Producer to:
    #       1. Have a Client ID
    #       2. Have a batch size of 100
    #       3. A Linger Milliseconds of 1 second
    #       4. LZ4 Compression
    #
    #       See: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    #
    p = Producer(
        {
            "bootstrap.servers": BROKER_URL,
            "client.id": "clientLucas",
            "linger.ms":1000, # tiempo que espera y acumula mensajes antes de mandar
            "compression.type":"lz4" ,
            "batch.num.messages": 10, # maximmo numero de mensajes a acmular antes de mandar
            #"queue.buffering.max.messages":"" (de todos los topicos)
            #"queue.buffering.max.kbytes":"" (de todos los topicos)
        }
    )
    start_time = datetime.now()
    curr_iteration = 0
    while True:
        p.produce(topic_name, Purchase().serialize())
        if curr_iteration % 1000 == 0:
            elapsed = (datetime.now() - start_time).seconds
            print(f"mensajes enviados: {curr_iteration} | total segundos: {elapsed}")
        curr_iteration+=1

def main():
    """Checks for topic and creates the topic if it does not exist"""
    create_topic(TOPIC_NAME)
    try:
        produce(TOPIC_NAME)
    except KeyboardInterrupt as e:
        print("shutting down")


def create_topic(client):
    """Creates the topic with the given topic name"""
    client = AdminClient({"bootstrap.servers": BROKER_URL})
    futures = client.create_topics(
        [NewTopic(topic=TOPIC_NAME, num_partitions=5, replication_factor=1)]
    )
    for _, future in futures.items():
        try:
            future.result()
        except Exception as e:
            pass


@dataclass
class Purchase:
    username: str = field(default_factory=faker.user_name)
    currency: str = field(default_factory=faker.currency_code)
    amount: int = field(default_factory=lambda: random.randint(100, 200000))

    def serialize(self):
        """Serializes the object in JSON string format"""
        return json.dumps(
            {
                "username": self.username,
                "currency": self.currency,
                "amount": self.amount,
            }
        )


if __name__ == "__main__":
    main()
