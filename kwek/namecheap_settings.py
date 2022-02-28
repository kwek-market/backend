
import os
from .general_settings import *

STATIC_URL = "/static/"
MEDIA_URL = "/asset/"

EMAIL_BACKEND_DOMAIN = "http://www.kwekapi.com"
STATICFILES_DIRS = [BASE_DIR, "static"]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = "/home/kwekxbyu/kwekapi.com/static/"
if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "asset")
else:
    MEDIA_ROOT = "/home/kwekxbyu/kwekapi.com/asset"


