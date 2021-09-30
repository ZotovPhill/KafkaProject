import json
import threading
import argparse

import socketio

from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
from kafka.admin import NewTopic
from kafka.structs import TopicPartition

sio = socketio.Client()
sio.connect("http://172.17.0.1:8000", socketio_path='/sio/socket.io/')


class Producer(threading.Thread):
    def __init__(self, topic, value):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.producer = None
        self.topic = topic
        self.value = value

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.producer = KafkaProducer(
            value_serializer=lambda m: json.dumps(m).encode("utf-8"),
            bootstrap_servers=["172.17.0.1:9092"],
        )

        self.produce()
        self.producer.close()
        self.stop()

    def produce(self):
        self.producer.send(self.topic, value=self.value)


class Consumer(threading.Thread):
    def __init__(self, topic, group, partition):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

        self.consumer = None
        self.topic = topic
        self.group = group
        self.partition = partition

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.consumer = KafkaConsumer(
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id=self.group,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            bootstrap_servers=["172.17.0.1:9092"],
            consumer_timeout_ms=1000,
        )
        self.consumer.assign([TopicPartition(self.topic, int(self.partition))])

        while not self.stop_event.is_set():
            for message in self.consumer:
                print(message)
                self.consume(message)
                if self.stop_event.is_set():
                    break
        
        self.consumer.close()
        sio.disconnect()

    def consume(self, message):
        print(message.value)


def run(consumer: Consumer):
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="Topic")
    parser.add_argument("--group", help="Group")
    parser.add_argument("--partition", help="Partition")
    args = parser.parse_args()

    admin = KafkaAdminClient(bootstrap_servers="172.17.0.1:9092")
    topic = admin.describe_topics([args.topic])[0]

    if topic["error_code"] != 0:
        topic = NewTopic(
            name=args.topic,
            num_partitions=1, 
            replication_factor=1
        )
        admin.create_topics([topic])
    if partitions := args.partition:
        partitions = partitions.split(",")
    else:
        topic = admin.describe_topics([args.topic])[0]
        partitions = [partition["partition"] for partition in topic["partitions"]]

    tasks = [
        consumer(args.topic, args.group, int(partition))
        for partition in partitions
    ]

    # Start thread for specidied partition or
    # for each partition of a Kafka topic consumer
    for t in tasks:
        t.start()


if __name__ == "__main__":
    run(Consumer)
