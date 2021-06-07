from faust import Record


class StatEvent(Record, serializer='json'):
    player: str
    damage: int
    healing: int

    def toString(self):
      return f'Player: {self.player}, Damage: {self.damage}, Healing: {self.healing}'


# Class for the Table, includes game count as well as average and top values for healing and damage
class PlayerAggregates:
    avg_dmg: int
    avg_heal: int
    top_dmg: int
    top_heal: int
    game_count: int

    def toString(self):
      return f'Average Damage: {self.avg_dmg}, Average Healing: {self.avg_heal}, Top Damage: {self.top_dmg}, Top Healing: {self.top_heal}, Total Games: {self.game_count}'

    def __init__(self):
      self.avg_dmg=0
      self.avg_heal=0
      self.top_dmg=0
      self.top_heal=0
      self.game_count=0

    def addEvent(self, event):
      new_aggregates = PlayerAggregates()
      
      new_aggregates.avg_dmg = (new_aggregates.avg_dmg*new_aggregates.game_count+event.damage)/(new_aggregates.game_count+1)
      new_aggregates.avg_heal = (new_aggregates.avg_heal*new_aggregates.game_count+event.healing)/(new_aggregates.game_count+1)
      
      if event.damage > new_aggregates.top_dmg:
        new_aggregates.top_dmg = event.damage
      if event.healing > new_aggregates.top_heal:
        new_aggregates.top_heal = event.healing

      new_aggregates.game_count +=  1
      return new_aggregates