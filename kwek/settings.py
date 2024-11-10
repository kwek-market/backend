# import imp
from decouple import config


stage = config("stage")
print("stage", stage)
RUNJOBS=False
if stage == "namecheap":
    from .namecheap_settings import *
elif stage == "heroku":
    from .heroku_settings  import *
elif stage == "render":
    from .render_settings  import *
else:
    from .dev_settings  import *