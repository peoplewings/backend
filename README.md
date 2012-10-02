# Peoplewings backend API

## Prerequisites

In order to work with this repo you will need the following tools installed in your system:

* Git
* Python 2.7 & Easy_install (optional just to install pip and other packages)
* Pip (easy_install pip)
* Virtual env 1.7+ (pip install virtualenv)
* Foreman (gem install foreman)

* PostgreSQL (optional just to test locally)
* Heroku toolbelt (optional, highly recommended!)


## Setup
* Create a virtual environment with *virtualenv*

    `$ virtualenv path/to/your/virtualenvs/virtual-env-name --distribute`

* Activate your virtual environment

    `$ source path/to/your/virtualenvs/virtual-env-name/bin/activate`

* Install requiriments using requirements.txt from this repo

    `$ pip install -r requiriments.txt`

* Start the gunicorn web server

    `$ foreman start`

Now you can open the application on 0.0.0.0:5000

Full reference can be found here:

* https://devcenter.heroku.com/articles/django
* https://devcenter.heroku.com/articles/heroku-postgres-dev-plan
* https://devcenter.heroku.com/articles/procfile
* https://devcenter.heroku.com/articles/error-codes
 
## API

IMPORTANT!! All urls start with /api/v1/
### Register (Joan):
 * Request:
    POST /newuser
    {"birthday_day":5, "birthday_month":3, "birthday_year":1999, "email":"asdadsqwe@asdasd.com", "email2":"asdadsqwe@asdasd.com", "first_name":"Ez", "gender":"M", "last_name":"Pz", "password1":"asdf"}
 * Response:
   * OK
     * 201 CREATED {"status": True, "code":"201", "data":"Your account has been succesfully..."}
   * NO 
     * 400 BAD REQUEST {"status": False, "code":"401", "error":{"error1":"aslkjdhkladn", "error2":"kajsdojbn"}}

### Activate (Joan):
 * Request:
    POST /activation
    {"activation_key":"asdkjbsjnskn"}
 * Response:
   * OK 
     * 201 CREATED {"status":True, "code":"201", "txt":"Your account has been activated"}
   * NO
     * 400 BAD REQUEST {"code": 810, "status": False, "error": "The activation key has been already used"}
     * 400 BAD REQUEST {"code": 811, "status": False, "error": "The provided key is not a valid key"}
     * 400 BAD REQUEST {"code": 812, "status": False, "error": "The provided key has expired"}
### Login (Joan):
 * Request:
    /POST /auth
     * 201 CREATED {username = "Joan", password = "asdfasdf"}
 * Response:
   * OK
     * 201 CREATED {"status":True, "code":"201", "token" = "ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
   * NO
     * 400 BAD REQUEST {"status":False, "code":"820", "error": "Username/password do not match any user in the system"}
     * 400 BAD REQUEST {"status":False, "code":"821", "error": "Inactive user"}
### Logout (Joan):
 * Request:
    /POST /noauth
    {}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
    * 204 NO CONTENT {"status":True, "code":"204"}
   * NO
    * 400 BAD REQUEST {"status":False, "code":"822", "error": "Can\'t logout"}
    

### Delete account (Joan) 03/09:

### Update account (Joan) 03/09:

### Forgot password (Joan) 03/09:

### View my profile (Eze) 05/09:

### Update my profile (Eze) 05/09:

### View another profile (Eze) 05/09:

### Upload image (Joan) 04/09:

### Crop image (Joan) (undefined):

### View my wings (Eze) 09/09:

### View one of my wings (Eze) 09/09:

### Create wing (Eze) 09/09:

### Update wing (Eze) 09/09:

### Search (wings) (undefined):

