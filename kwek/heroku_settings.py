

import os
from .general_settings import *
import django_heroku

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATIC_URL = "/static/"
# MEDIA_URL = "/asset/"

# STATICFILES_DIRS = [BASE_DIR, "static"]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
# STATIC_ROOT = "/home/kwekxbyu/kwekapi.com/static/"
# if DEBUG:
#     MEDIA_ROOT = os.path.join(BASE_DIR, "asset")
# else:
#     MEDIA_ROOT = "/home/kwekxbyu/kwekapi.com/asset"
BACKEND_DOMAIN = "https://kwekapi.herokuapp.com"
# ?/////////////////////////////Heroku
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_ROOT  = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# ?/////////////////////////////Heroku

django_heroku.settings(locals())

