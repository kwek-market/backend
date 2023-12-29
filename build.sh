pip install --upgrade pip
pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python manage.py collectstatic
deactivate