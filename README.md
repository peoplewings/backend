# Peoplewings backend API

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
 


## API

IMPORTANT!! All urls start with /api/v1/
### Register:
 - Request:
    POST /newuser
    {"birthday_day":5, "birthday_month":3, "birthday_year":1999, "csrfmiddlewaretoken":"adsasd", "email":"asdadsqwe@asdasd.com", "email_2":"asdadsqwe@asdasd.com", "first_name":"Ez", "gender":"M", "last_name":"Pz", "password1":"asdf"}
 - Response:
    201 CREATED
    {"status": True, "code":"201", "data":"Your account has been succesfully..."}
    {"status": False, "code":"401", "error":{"error1":"aslkjdhkladn", "error2":"kajsdojbn"}}

### Activate:
 - Request:
    /POST 
 - Response:
    
    {"status":True, "code":"201", "txt":"Your account has been activated"}
    {"status": False, "code":"401", "error":{"error1":"aslkjdhkladn", "error2":"kajsdojbn"}}
### Login
 - Request:

 - Response:

### Logout:
 - Request:

 - Response:

### Unregister:
 - Request:

 - Response:

### Update user (account settings):
 - Request:

 - Response:

### Forgot password:
 - Request:

 - Response:

### Needed environment variables
