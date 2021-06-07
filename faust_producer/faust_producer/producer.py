from confluent_kafka import Producer
from json import dumps
from time import sleep
import socket
import random

# Hard coded configs
# TODO: Replace with command line arguments or config file
# Outlaws players, Go Houston!
player_name_array = ['Jake', 'Hydration', 'Happy', 'Crimzo', 'Piggy','Danteh', 'KSF', 'Dreamer', 'Joobi', 'Jjanggu'] 
# Number of events to be generated
number_of_events = 10
sleep_length = 2


class StatEvent:
  def __init__(self, player, damage, healing):
    self.player = player
    self.damage = damage
    self.healing = healing

conf = {
  "bootstrap.servers": "localhost:9092",
  "client.id": socket.gethostname()
}

producer = Producer(conf)

for i in range(number_of_events):
  player = random.choice(player_name_array)
  damage = random.randint(1000,6000)
  healing = random.randint(1000,6000)
  event = {
    'player': player,
    'damage': damage,
    'healing': healing
  }
  producer.produce('player_stats', key=player, value=dumps(event))
  sleep(sleep_length)

producer.flush()