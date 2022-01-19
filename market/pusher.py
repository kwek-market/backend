import pusher

pusher_client = pusher.Pusher(
  app_id='1334609',
  key='bba1486f3390745bca34',
  secret='4dd1bd62d587c4eb8924',
  cluster='mt1',
  ssl=True
)

def PushToClient(channel:str, data:dict):
    pusher_client.trigger(channel, channel, data)