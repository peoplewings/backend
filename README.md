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
    POST /newuser/
    {"birthdayDay":5, "birthdayMonth":3, "birthdayYear":1999, "email":"joan@peoplewings.com", "repeatEmail":"joan@peoplewings.com", "firstName":"Ez", "gender":"Male", "lastName":"Pz", "password":"asdf"}
 * Response:
   * OK
     * 201 CREATED {"status": True, "code":"201", "data":"Your account has been succesfully..."}
   * NO 
     * 400 BAD REQUEST {"status": False, "code":"401", "error":{"error1":"aslkjdhkladn", "error2":"kajsdojbn"}}
     * 400 BAD REQUEST {"code": 813, "error": "The email is already being used", "status": false}

### Activate (Joan):
 * Request:
    POST /activation/
    {"activationKey":"asdkjbsjnskn"}
 * Response:
   * OK 
     * 201 CREATED {"status":True, "code":"201", "txt":"Your account has been activated"}
   * NO
     * 400 BAD REQUEST {"code": 810, "status": False, "error": "The activation key has been already used"}
     * 400 BAD REQUEST {"code": 811, "status": False, "error": "The provided key is not a valid key"}
     * 400 BAD REQUEST {"code": 812, "status": False, "error": "The provided key has expired"}

### Login (Joan):
 * Request:
    /POST /auth/
     * 201 CREATED {username = "Joan", password = "asdfasdf"}
 * Response:
   * OK
     * 201 CREATED {"status":True, "code":"201", "token" = "ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
   * NO
     * 400 BAD REQUEST {"status":False, "code":"820", "error": "Username/password do not match any user in the system"}
     * 400 BAD REQUEST {"status":False, "code":"821", "error": "Inactive user"}

### Logout (Joan):
 * Request:
    /POST /noauth/
    {}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
    * 204 NO CONTENT {"status":True, "code":"204"}
   * NO
    * 400 BAD REQUEST {"status":False, "code":"822", "error": "Can\'t logout"}
    
### View my account (Joan):
 * Request:
    /GET /accounts/me
    {}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
    * 200 OK {"status":True, "code":"200", "data":[{"dateJoined": "2012-09-28T10:49:53.497530+00:00", "email": "fr33d4n@gmail.com", "firstName": "Ez", "lastLogin": "2012-10-02T11:35:04.505081+00:00", "lastName": "Pz", "password": "pbkdf2_sha256$10000$t4RMJPP649ZE$bhUiYcVcteTXYcdBDba5AjH9DM6ckBI+SjhGicelWAs="}]}
   * NO (Method not allowed and unauthorized)
    
### Delete account (Joan):
 * Request:
    /POST /accounts/me/
    {"isActive" = false}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
     * 204 NO CONTENT
   * NO (Method not allowed and unauthorized)
     * 400 BAD REQUEST {"code": 410, "data": "The account does not exist", "status": false}
     * 400 BAD REQUEST {"code": 400, "data": "Invalid parameters", "status": false}

### Update account (Joan) (undefined):
 * Need specifications.

### Request Forgot password (Joan):
 * Request:
    /POST /forgot/
    {"email" = "joan@peoplewings.com"}
 * Response:
   * OK
     * 202 CREATED {"code": 202, "data": "Email sent", "status": true}
   * NO 
     * 400 BAD REQUEST {"code": 400, "data": "Invalid email", "status": false}
     * 400 BAD REQUEST {"code": 777, "error": {"email": ["This field is required."]}, "status": false}

### Check if the resetPassword link is valid (Joan):
 * Request:
    /GET /forgot/?forgotToken=f27c26f21835e557892970011450962c0331d712
    {}
 * Response:
   * OK
     * 200 OK {"code": 200, "data": "The link is valid", "status": true}
   * NO 
     * 400 BAD REQUEST {"code": 400, "data": "Invalid link", "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}
     * 400 BAD REQUEST {"code": 412, "data": "The key has expired", "status": false}

### Submit new password (Joan):
 * Request:
    /POST /forgot/
    {"forgotToken":"f27c26f21835e557892970011450962c0331d712", "newPassword":"qwerty"} 
 * Response:
   * OK
     * 200 OK {"code": 200, "data": "Password changed", "status": true}
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": "Invalid link", "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": {"params": ["Bad parameters"]}, "status": false}

### View my profile (Eze) 05/09:
 - Request:
    /GET /profiles
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 - Response:
   - OK
     - 200 OK 

   - NO
     - 401 UNAUTHORIZED {"status":False, "code":"401", "error": "Unauthorized"}

### Update my profile (Eze) 05/09:
 - Request:
    /POST /profiles/me
    {"X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
    { COMPLETAR }
 - Response:
   - OK
     - 202 Accepted {"code": 204, "data": "Updated", "status": true}

### View another profile (Eze) 05/09:
 - Request:
    /GET /profiles/?user=19
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 - Response:
   - OK
     - 200 OK 

   - NO
     - 401 UNAUTHORIZED {"status":False, "code":"401", "error": "Unauthorized"}

### View a list of Profiles (Ezequiel) 05/09:
 - Request:
    /GET /profiles/?from=1&to=4
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 - Response:
   - OK
     - 200 OK 
     
   - NO
     - 401 UNAUTHORIZED {"status":False, "code":"401", "error": "Unauthorized"}

### Upload image (Joan) 04/09:

### Crop image (Joan) (undefined):

### View my wings (Eze) 09/09:

### View one of my wings (Eze) 09/09:

### Create wing (Eze) 09/09:

### Update wing (Eze) 09/09:

### Search (wings) (undefined):


### Needed environment variables

