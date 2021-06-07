import faust
from json import loads, dumps
from models import PlayerAggregates, StatEvent

app = faust.App(
    'owl-stats-stream-process',
    broker='kafka://localhost:9092',
    value_serializer='raw',
)

player_stats_topic = app.topic('player_stats', value_type=StatEvent)
player_aggregates = app.Table(
    'player_aggregates',
    default=(lambda: {
        'avg_dmg': 0,
        'avg_heal': 0,
        'top_dmg': 0,
        'top_heal': 0,
        'game_count': 0,
    })
)


@app.agent(player_stats_topic)
async def processStatEvent(player_stats):
    async for stat_event in player_stats:
        # Assign player name
        player = stat_event.player
        current_aggregates = player_aggregates[player]
            
        current_aggregates['avg_dmg'] = (current_aggregates['avg_dmg']*current_aggregates['game_count']+stat_event.damage)/(current_aggregates['game_count']+1)
        current_aggregates['avg_heal'] = (current_aggregates['avg_heal']*current_aggregates['game_count']+stat_event.healing)/(current_aggregates['game_count']+1)
        
        if stat_event.damage > current_aggregates['top_dmg']:
            current_aggregates['top_dmg'] = stat_event.damage
        if stat_event.healing > current_aggregates['top_heal']:
            current_aggregates['top_heal'] = stat_event.healing

        current_aggregates['game_count'] +=  1
        player_aggregates[player] = current_aggregates

        print('Processed new event')
        print(stat_event.toString())
        print(f'New stats for player {player}')
        print(dumps(current_aggregates))

