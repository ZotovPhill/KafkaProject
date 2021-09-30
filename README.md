## KAFKA TRAIN PROJECT

## How to build

    docker-compose build

## How to run

    docker-compose up

## Together

    docker-compose up -d --build

## Application config

* zookeeper
* kafka
* kowl

### Virtual environment

At root ./KafkaProject folder run command to create virtual environment

    python -m venv .venv

To activate run command

    source .venv/bin/activate

### Dependencies

For local kafka testing install poetry dependency manager on your local machine.
To install dependincies run 

    poetry install


After installing dependencies and activating virtual environment you ready to start kafka producer and consumers

### Producer

    python producer.py

### Consumer

    python consumer.py --partition <number of partition>
