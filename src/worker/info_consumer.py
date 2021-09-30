from main import Consumer, sio, run


class InfoConsumer(Consumer):
    def consume(self, message):
        sio.emit("packet", {"data": message.value})

if __name__ == "__main__":
    run(InfoConsumer)