APP_NAME=worker
CONSUMER_ROOT_FOLDER=src/worker
KAFKA_SYSTEM_FOLER=system/kafka-docker
PARTITIONS?=1
TOPIC?=test
BOOTSTRAP_SERVER?=localhost:9092
ZOOKEEPER_SERVER?=zookeeper:2181

build:
	docker build -t $(APP_NAME) -f ./system/$(APP_NAME)/Dockerfile .

create-topic:
	cd $(KAFKA_SYSTEM_FOLER) 
		 -c "cd bin && kafka-topics.sh --create --partitions $(PARTITIONS) --bootstrap-server $(BOOTSTRAP_SERVER) --topic $(TOPIC)"

delete-topic:
	cd $(KAFKA_SYSTEM_FOLER) 
	docker exec -it kafka sh -c "cd bin && kafka-topics.sh --zookeeper $(ZOOKEEPER_SERVER) --delete --topic $(TOPIC)"

kafka-consumer-parser:
	docker run -v /src:/src:z --restart always -d $(APP_NAME) python $(CONSUMER_ROOT_FOLDER)/stock_parser_consumer.py --topic stock_parser --group parser

kafka-consumer-quotes:
	docker run -d $(APP_NAME) python $(CONSUMER_ROOT_FOLDER)/info_consumer.py --topic quotes --group info --partition 0,1,2

kafka-consumer-news:
	docker run -d $(APP_NAME) python $(CONSUMER_ROOT_FOLDER)/info_consumer.py --topic news --group info

rebuild-consumers:
	make build
	make kafka-consumer-parser
	make kafka-consumer-quotes
	make kafka-consumer-news