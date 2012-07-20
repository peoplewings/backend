# Peoplewings project reference

## Prerequisites

In order to work with this repo you will need the following tools installed in your system:

- Git
- Python 2.7 & Easy_install (optional just to install pip and other packages)
- Pip (easy_install pip)
- Virtual env 1.7+ (pip install virtualenv)
- Foreman (gem install foreman)

- PostgreSQL (optional just to test locally)
- Heroku toolbelt (optional, highly recommended!)


## Setup
- Create a virtual environment with *virtualenv*

    `$ virtualenv path/to/your/virtualenvs/virtual-env-name --distribute`

- Activate your virtual environment

    `$ source path/to/your/virtualenvs/virtual-env-name/bin/activate`

- Install requiriments using requirements.txt from this repo

    `$ pip install -r requiriments.txt`

- Start the gunicorn web server

    `$ foreman start`

Now you can open the application on 0.0.0.0:5000

Full reference can be found here:

- https://devcenter.heroku.com/articles/django
- https://devcenter.heroku.com/articles/heroku-postgres-dev-plan
- https://devcenter.heroku.com/articles/procfile
- https://devcenter.heroku.com/articles/error-codes
 


## Development notes

Find the project documentation in [Documentation](/88fingerskid/peoplewings/src/master/src/doc/documentation.md/ "Peoplewings documentation")

  

### Needed environment variables
