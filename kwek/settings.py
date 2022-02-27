import imp
from pathlib import Path
import os
from dotenv import load_dotenv
from decouple import config
import django_heroku


stage = config("stage")
print("stage", stage)

if stage == "namecheap":
    from .namecheap_settings import *
elif stage == "heroku":
    from .heroku_settings  import *
else:
    from .dev_settings  import *