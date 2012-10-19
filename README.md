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
sad 
## API
dfds
IMPORTANT!! All urls start with /api/v1/

There are some standard error messages:

* 200 OK {"code": 410, "error": {"errors": {"gender": ["This field is required."], "lastName": ["This field is required."]}, "msg": "Error in some fields"}, "status": false}
* 200 OK {"code": 411, "error": {"msg": "No JSON could be decoded"}, "status": false}
* 200 OK {"code": 412, "error": {"msg": "Method not allowed"}, "status": false}
* 200 OK {"code": 413, "error": {"msg": "Unauthorized"}, "status": false}


### Register (Joan):
 * Request:
    POST /newuser/
    {"birthdayDay":5, "birthdayMonth":3, "birthdayYear":1999, "email":"joan@peoplewings.com", "repeatEmail":"joan@peoplewings.com", "firstName":"Ez", "gender":"Male", "lastName":"Pz", "password":"asdf"}
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"email": "joan@peoplewings.com", "msg": "Account created"}, "status": true}
   * NO
     * 200 OK {"code": 400, "error": {"msg": "The email is already being used"}, "status": false}
     * 200 OK {"code": 400, "error": {"msg": "Emails don't match"}, "status": false}

### Activate (Joan):
 * Request:
    POST /activation/
    {"activationKey":"9286095aa048bf4c28369830520263d135f841d1"}
 * Response:
   * OK 
     * 200 OK {"code": 200, "data": {"msg": "Account activated"}, "status": true}
   * NO
     * 200 OK {"code": 400, "error": {"msg": "The activation key has been already used"}, "status": false}
     * 200 OK {"code": 400, "error": {"msg": "The activation key is not a valid key"}, "status": false}
     * 200 OK {"code": 400, "error": {"msg": "The provided key has expired"}, "status": false}

### Login (Joan):
 * Request:
    /POST /auth/
     {username = "Joan", password = "asdfasdf"}
     {username = "joan@peoplewings.com, password = "asdf", remember="on"} (This call keeps you logged in in the system, forever)
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"msg": "Logged in", "x-auth-token": "88a04fa420dc2b3734be743e3f4dc0475d1eedf4a29b75330c4d971d11f3d898e14302d773bc5500"}, "status": true}
   * NO
     * 200 OK {"code": 400, "error": {"msg": "Username/password do not match any user in the system"}, "status": false}
     * 200 OK {"code": 400, "error": {"msg": "Inactive user"}, "status": false}

### Request Forgot password (Joan):
 * Request:
    /POST /forgot/
    {"email" = "joan@peoplewings.com"}
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"msg": "Email sent"}, "status": true}
   * NO 
     * 200 OK {"code": 400, "error": {"msg": "Invalid email"}, "status": false}

### Check if the resetPassword link is valid (Joan):
 * Request:
    /GET /forgot/?forgotToken=f27c26f21835e557892970011450962c0331d712
    {}
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"msg": "The link is valid"}, "status": true}
   * NO 
     * 200 OK {"code": 400, "error": {"msg": "Not a key"}, "status": false}
     * 200 OK {"code": 400, "error": {"msg": "The key has expired"}, "status": false}

### Submit new password (Joan):
 * Request:
    /POST /forgot/
    {"forgotToken":"f27c26f21835e557892970011450962c0331d712", "newPassword":"qwerty"} 
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"msg": "Password changed"}, "status": true}
   * NO 
     * 200 OK {"code": 400, "error": {"msg": "Not a key"}, "status": false}
     * 200 OK {"code": 400, "error": {"msg": "The key has expired"}, "status": false}

### Logout (Joan):
 * Request:
    /POST /noauth/
    {}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
    * 200 OK {"code": 200, "data": {"msg": "Logout complete"}, "status": true}
   * NO
    * 200 OK {"code": 400, "error": {"msg": "Can't logout"}, "status": false}
    
### View my account (Joan):
 * Request:
    /GET /accounts/me
    {}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
    * 200 OK {"code": 200, "data": {"email": "fr33d4n@gmail.com", "firstName": "Ez", "lastName": "Pz", "password": "uqdh891288yuaidsbh"}, "msg": "Account shown", "status": true}
   * NO 
    
### Delete my account (Joan):
 * Request:
    /DELETE /accounts/me/
    {"current_password":"asdf"}
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"msg": "Account deleted"}, "status": true}
   * NO 

### Update account (Joan):
 * Request:
    /PUT /accounts/me/
    {"current_password":"asdf", "resource":{"email":"asdf", "password":"qwert", "lastName":"lol"}} All these minus current_password are optional, you can always have 1 field or more
    X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145
 * Response:
   * OK
     * 200 OK {"code": 200, "data": {"email": "joan@peoplewings.com", "firstName": "Ez", "lastName": "DangReGu", "msg": "Account updated"}, "status": true}
   * NO
     * 200 OK {"code": 200, "errors": {"password": ["Incorrect current password"]}, "msg": "Cannot update", "status": false}


### View a list of Profiles (Ezequiel):
 * Request:
    /GET profiles/
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 * Response:
   * OK
     * 200 OK 
      [
        {"age": 22, "allAboutYou": "lalalal", ...},
        {"age": 24, "allAboutYou": "lelelel", ...},
        ...
      ]

### View my profile (Eze):
 * Request:
    /GET profiles/me/
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 * Response:
   * OK
     * 200 OK 
      {
          "age": 22, "allAboutYou": "ASDF", "avatar": "ASDF", "birthday": "1990-02-01", "civilState": "",
          "company": "", 
          "current": 
            {
              "city": "Barcelona",
              "country": "Spain",
              "region": "Catalonia"
            },
          "education": 
            [
              {
                "degree": "Computer Science",
                "name": "University of Reading"
              },
              {
                "degree": "Artificial Intelligence",
                "name": "University of London"
              }
            ],
          ....
      }
   * NO
     * 403 FORBIDDEN {"code": 413, "msg": "Error: operation not allowed", "status": false}

### Update my profile (Eze):
 * Request:
    /PUT profiles/me/
    {"X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
    {
      "allAboutYou": "All about me", 
      "current": {"city": "Barcelona", "country": "Spain", "region": "Catalonia"}, 
      "education": 
        [
          {"degree": "Computer Science", "name": "University of Reading"}, 
          {"degree": "Artificial Intelligence", "name": "University of London"}
        ], 
      "hometown": {"city": "Bilbao",  "country": "Spain", "region": "Pais Vasco"},
      "instantMessages": 
        [
          {"name": "Skype", "username": "My IM Username"}, 
          {"name": "Whatsapp", "username": "My IM Username 2"}
        ], 
      "languages": 
        [
          {"level": "Expert", "name": "English"}, 
          {"level": "Beginner", "name": "Spanish"}
        ],
      "otherLocations": 
      [
        {"city": "Barcelona", "country": "Spain", "region": "Catalunya"}, 
        {"city": "Madrid", "country": "Spain", "region": "Madrid"}, 
        {"city": "Alava", "country": "Spain", "region": "Pais Vasco"}
      ], 
      "socialNetworks": 
      [
        {"name": "Facebook", "username": "Facebook Username"}, 
        {"name": "Twitter", "username": "Twitter Username"}
      ]
    }

 * Response:
   * OK
     * 202 Accepted {"code": 200, "msg": "Your profile has been successfully updated.", "status": true}
   * NO
     * 403 FORBIDDEN {"code": 413, "msg": "Error: anonymous users have no profile.", "status": false}

### View another profile (Eze):
 * Request:
    /GET profiles/17/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * OK
     * 200 OK 
      {
        "age": 24, "allAboutYou": "ASDF", "avatar": "ASDF", "birthday": "1988-02-01", "civilState": "",
        "company": "", 
        "current": 
          {
            "city": "Barcelona",
            "country": "Spain",
            "region": "Catalonia"
          },
        "education": 
          [
            {
              "degree": "Philosophy",
              "name": "Universidad de Madrid"
            }
          ],
        ....
      }
          
   * NO
     * 401 UNAUTHORIZED {"status":False, "code":"401", "error": "Unauthorized"}


### Upload image (Joan) (W8 Sergi):

### Crop image (Joan) (W8 Sergi):

### View my accomodations (Joan):
 * Request:
    /GET /profiles/me/accomodations/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * OK
     * 200 OK
        [
          {
            "about": "",
            "additionalInformation": "",
            "address": "",
            ...
          },
          {
            "about": "",
            "additionalInformation": "",
            "address": "",
            ....
          },
          {
            "about": "",
            "additionalInformation": "",
            "address": "",
            ...
          }
        ]
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": "Invalid link", "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": {"params": ["Bad parameters"]}, "status": false}

### View one of my accomodations (Eze):
 * Request:
    /GET /profiles/me/accomodations/20/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * 200 OK
      {
        "about": "",
        "additionalInformation": "",
        "address": "",
        ...
      }
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}

### View an accomodation of another user (Eze):
 * Request:
    /GET /profiles/17/accomodations/20/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * 200 OK
      {
        "about": "",
        "additionalInformation": "",
        "address": "",
        ...
      }
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": "Unauthorized", "status": false}

### Create Accomodation (Eze):
 * Request:
    /POST /profiles/me/accomodations/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
    {
      "about": "",
      "additionalInformation": "",
      "address": "",
      ...
    }

 * Response:
   * 200 CREATED {"code": 204, "data": "Updated", "status": true}
      
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}
     * 400 BAD REQUEST {"code": 777, "errors": "Unauthorized", "status": false}

### Update accomodation (Eze):
 * Request:
    /POST /profiles/me/accomodations/20/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
    {
      "about": "",
      "additionalInformation": "",
      "address": "",
      ...
    }

 * Response:
   * 204 NO CONTENT {"code": 204, "data": "Updated", "status": true}
      
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}

### Delete accomodation (Eze):
 * Request:
    /DELETE /profiles/me/accomodations/20/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * 204 NO CONTENT {"code": 204, "data": "Wing deleted", "status": true}
      
   * NO 
     * 400 BAD REQUEST {"code": 777, "errors": {"forgotToken": ["This field is required"]}, "status": false}

### Search wings (undefined):

