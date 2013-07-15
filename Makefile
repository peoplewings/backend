
pull.helper:
	git pull

pull: pull.helper apply_changes

apply_changes:
	python manage.py apply_changes

run:
	~/Virtualenvs/ppw-backend/bin/python2.7 manage.py runserver 0.0.0.0:5000

fixtures:
	python loadfixtures.py fake notifications

virtualenv:
	source ~/Virtualenvs/ppw-backend/bin/activate \n cd `pwd`

install:
	mkdir ~/Virtualenvs
	virtualenv ~/Virtualenvs/ppw-backend --distribute
	pip install -r requirements.txt

install.helper:
	python manage.py syncdb

install2: install.helper fixtures apply_changes run
