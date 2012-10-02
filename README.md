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
   - OK
     - 201 CREATED {"status": True, "code":"201", "data":"Your account has been succesfully..."}
   - NO 
     - 400 BAD REQUEST {"status": False, "code":"401", "error":{"error1":"aslkjdhkladn", "error2":"kajsdojbn"}}

### Activate:
 - Request:
    POST /activation
    {"activation_key":"asdkjbsjnskn"}
 - Response:
   - OK 
     - 201 CREATED {"status":True, "code":"201", "txt":"Your account has been activated"}
   - NO
     - 400 BAD REQUEST {"code": 810, "status": False, "error": "The activation key has been already used"}
     - 400 BAD REQUEST {"code": 811, "status": False, "error": "The provided key is not a valid key"}
     - 400 BAD REQUEST {"code": 812, "status": False, "error": "The provided key has expired"}
### Login
 - Request:
    /POST /auth
     - 201 CREATED {username = "Joan", password = "asdfasdf"}
 - Response:
   - OK
     - 201 CREATED {"status":True, "code":"201", "token" = "ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
   - NO
     - 400 BAD REQUEST {"status":False, "code":"820", "error": "Username/password do not match any user in the system"}
     - 400 BAD REQUEST {"status":False, "code":"821", "error": "Inactive user"}
### Logout:
 - Request:
    /POST /noauth
    {"token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
 - Response:
   - OK
    - 204 NO CONTENT {"status":True, "code":"204"}
   - NO
    - 400 BAD REQUEST {"status":False, "code":"822", "error": "Can\'t logout"}
    

### Unregister: (delete account)
 - Request:

 - Response:

### Update user (account settings):
 - Request:

 - Response:

### Forgot password:
 - Request:

 - Response:

### View all Profiles (Ezequiel)
 - Request:
    /GET /profiles
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
    "from": 1, "to": 4
 - Response:
   - OK
     - 200 OK 
     [
     {"age": 12, "allAboutYou": "", "avatar": "/static/img/blank_avatar.jpg", "birthday": "2000-03-10", "civilState": "", "company": "", "emails": "", "enjoyPeople": "", "gender": "M", "id": "3", "incredible": "", "inspiredBy": "", "interestedIn": "", "mainMission": "", "movies": "", "nameToShow": "eze", "occupation": "", "otherPages": "", "personalPhilosophy": "", "phone": "", "placesGonnaGo": "", "placesLivedIn": "", "placesVisited": "", "placesWannaGo": "", "politicalOpinion": "", "pwOpinion": "", "pwState": "Y", "quotes": "", "religion": "", "sharing": "", "showBirthday": "N", "sports": "", "user": "/api/v1/account/5/"}
     , 
     {"age": 12, "allAboutYou": "", "avatar": "/static/img/blank_avatar.jpg", "birthday": "2000-04-09", "civilState": "", "company": "", "emails": "", "enjoyPeople": "", "gender": "M", "id": "5", "incredible": "", "inspiredBy": "", "interestedIn": "", "mainMission": "", "movies": "", "nameToShow": "aaaa", "occupation": "", "otherPages": "", "personalPhilosophy": "", "phone": "", "placesGonnaGo": "", "placesLivedIn": "", "placesVisited": "", "placesWannaGo": "", "politicalOpinion": "", "pwOpinion": "", "pwState": "W", "quotes": "", "religion": "", "sharing": "", "showBirthday": "F", "sports": "", "user": "/api/v1/account/7/"}
     , 
     {"age": 16, "allAboutYou": "", "avatar": "/static/img/blank_avatar.jpg", "birthday": "1995-12-07", "civilState": "", "company": "", "emails": "", "enjoyPeople": "", "gender": "M", "id": "6", "incredible": "", "inspiredBy": "", "interestedIn": "", "mainMission": "", "movies": "", "nameToShow": "d", "occupation": "", "otherPages": "", "personalPhilosophy": "", "phone": "", "placesGonnaGo": "", "placesLivedIn": "", "placesVisited": "", "placesWannaGo": "", "politicalOpinion": "", "pwOpinion": "", "pwState": "W", "quotes": "", "religion": "", "sharing": "", "showBirthday": "F", "sports": "", "user": "/api/v1/account/8/"}
     ]
   - NO
     - 401 UNAUTHORIZED {"status":False, "code":"401", "error": "Unauthorized"}

### View one Profile (Ezequiel)
 - Request:
    /GET /profiles/19
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 - Response:
   - OK
     - 200 OK {"age": 22, "allAboutYou": "", "avatar": "/static/img/blank_avatar.jpg", "birthday": "1990-02-01", "civilState": "", "company": "", "emails": "", "enjoyPeople": "", "gender": "M", "id": "19", "incredible": "", "inspiredBy": "", "interestedIn": "", "mainMission": "", "movies": "", "nameToShow": "lala", "occupation": "", "otherPages": "", "personalPhilosophy": "", "phone": "", "placesGonnaGo": "", "placesLivedIn": "", "placesVisited": "", "placesWannaGo": "", "politicalOpinion": "", "pwOpinion": "", "pwState": "N", "quotes": "", "religion": "", "sharing": "", "showBirthday": "F", "sports": "", "user": "/api/v1/account/21/"}
   - NO
     - 401 UNAUTHORIZED {"status":False, "code":"401", "error": "Unauthorized"}

### Edit my Profile (Ezequiel)
 - Request:
    /POST /profiles/19
    {"X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
    {"pw_state":"Y"}
 - Response:
   - OK
     - 202 Accepted {"code": 204, "data": "Updated", "status": true}


### Needed environment variables
