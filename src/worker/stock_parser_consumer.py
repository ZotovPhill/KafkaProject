import json

from main import Consumer, Producer, run


class StockInfoProducer(Producer):
    def produce(self):
        room_id = {"room_id": self.value["room_id"]}
        for value in self.value["info"]:
            info = {"info": value}
            self.producer.send(self.topic, room_id | info)


class StockParserConsumer(Consumer):
    def consume(self, message):
        with open("src/worker/fixtures.json", "r") as data:
            data = json.load(data)
            tasks = [
                StockInfoProducer("quotes", message.value | {"info": data["quotes"]}),
                StockInfoProducer("news", message.value | {"info": data["news"]}),
            ]
            for task in tasks:
                task.start()


if __name__ == "__main__":
    run(StockParserConsumer)
