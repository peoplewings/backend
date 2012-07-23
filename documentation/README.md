# Peoplewings project documentation

## South setup
 - Initially, install South from requirements.txt
 - Create an initial migration for an app, for example "people":
 	`$ python manage.py schemamigration people --initial`
 - From now on, every time a model in that app is modified, to apply changes to the database do the following:
 	- create a migration with the changes:
 		`$ python manage.py schemamigration people --auto`
 	- apply migration:
 		`$ python manage.py migrate people`

## Backend API

- url1
- url2
