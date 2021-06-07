# Faust Demo
The purpose of this project is to experiment with the [Faust Python library](https://faust.readthedocs.io/en/latest/introduction.html), which provides a simple, pure python implemenation of stream processing features similar to technologies like kstreams.

This project reads a stream of `player_stats`, which represent stats from a game of [Overwatch](https://playoverwatch.com/en-us/), including `player_name`, `damage` and `healing` for that game. The app records the average and top values for healing and damage of a player, persisting these aggregates to [Table](https://faust.readthedocs.io/en/latest/userguide/tables.html).

Eventually, the plan will be to consume [Overwatch League StatsLab Data](https://overwatchleague.com/en-us/statslab). For now, the producer will generate a small number of messages with random values. This data includes timestamps, allowing for experiments with windowing using the [`relative_to_field()`](https://faust.readthedocs.io/en/latest/userguide/tables.html#how-to) function

All objects including topics, streams and tables are partitioned by `player_name` 

As these events are processed, the data from the event and the new aggregates are printed.

## Getting started
### Prereqs
- [Python 3.6+](https://www.python.org/downloads/)
- [Global Faust Install](https://faust.readthedocs.io/en/latest/userguide/installation.html)
- [Poetry](https://python-poetry.org/docs/)
- [Docker and Docker Compose](https://docs.docker.com/get-docker/)

## Project Structure
- faust-producer: A simple python/poetry project to read csv data and stream it to a Kafka topic. Currently generates random data using a hard coded number of records. Uses the [Confluent python client](https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html)
- faust-app:  The Faust application reading from the Kafka topic 
- kafka: Docker-compose for starting the [Confluent Platform](https://docs.confluent.io/platform/current/quickstart/ce-docker-quickstart.html) locally. This runs Kafka as well as the [Confluent Control Center](https://docs.confluent.io/platform/current/control-center/index.html#control-center), a web based UI for managing a Kafka Cluster as well as other components of the Confluent Platform including Schema Registry, KsqlDB and Kafka Connect 

## Setup Kafka  Topics
Both the producer and Faust application utilize Kafka running on localhost. If you do not have a local version of Kafka running, you can run `docker-compose up`in the Kafka directory.

Faust assumes that the topics it is reading from already exist, so you have to pre-create them. If you are running the Confluent Platform using the docker-compose in the `kafka` directory, you can create this topic through the UI available at `localhost:9021`. Create a topic `player_stats`. When creating, set the number of partitions you want. Remmeber that you can only have as many parallel workers as you do partitions. I set mine to 4. Due to a [Faust bug](https://github.com/robinhood/faust/issues/325) you have to also manually create the changelog topic for the table. This topic is called `owl-stats-stream-process-player_aggregates-changelog` and it must be created with the same number of partitions as the `player_stats` topic. A workaround for this bug has been [posted here](https://github.com/robinhood/faust/issues/358#issuecomment-722891283), but I have not tested it yet. 

## Starting the Faust App
The Faust application assumes that the docker-compose from the `kafka` dir is running, or that some other Kafka instance is running on Localhost with the standard Broker and Zookeeper ports. It will read messages written to the `player_stats` topic. 

One of the advantages of Faust is it's automatic scalability, up to the number of partitions in the topic. To demonstrate this, first run the project with just one instace and then push data. You should see all data processed by that single instance. Then, start 1 or more other instances in separate process before sending more data. You should all instances processing the data separately now, with each player being processed by a single instance. To start an instance use:

```
faust -A owl_processor worker -l info
```

This starts an instance that consumes the web-port 6066. Each worker needs it's own web port so start a second worker using 

```
faust -A owl_processor worker -l info  --web-port=6067
```

Subsequent workers can be started by modifying the port number. Remember, you can only run as many workers as you have partitions in your `player_stats` Kafka topic. Additional workers will be idle. 

## Starting the Producer
Currently the producer producers a hard-coded number of events, assigning a random player name from a provided range and random stats. Modifying this value of `number_of_events` will generate more events. The `sleep_length` variable controls how long in seconds the process will wait between sending messages. The application assumes that the docker-compose from the `kafka` dir is running, or that some other Kafka instance is running on Localhost with the standard Broker and Zookeeper ports.

Run the application with:

```
poetry install
cd faust_producer/faust_producer
poetry run python producer.py
```

This should send events. If you have your Faust worker or workers currently running, you should see these events processed in real time. Otherwise, the faust worker will process new events on startup. 