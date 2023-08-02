import imp
from decouple import config


stage = config("stage")
print("stage", stage)

if stage == "namecheap":
    from .namecheap_settings import *
elif stage == "heroku":
    from .heroku_settings  import *
else:
    from .dev_settings  import *