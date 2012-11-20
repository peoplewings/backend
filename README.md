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
    {"email" : "joan@peoplewings.com"}
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
    {X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145}
 * Response:
   * OK
    * 200 OK {"code": 200, "data": {"msg": "Logout complete"}, "status": true}
   * NO
    * 200 OK {"code": 400, "error": {"msg": "Can't logout"}, "status": false}
    
### View my account (Joan):
 * Request:
    /GET /accounts/me
    {X-AUTH-TOKEN:ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145}
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


### View my profile (Eze):
 * Request:
    /GET profiles/me/
    "X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"
 * Response:
   * OK
     * 200 OK 
      {
          "code":200,
          "data": {
            "age":13,
            "allAboutYou": "say whaaaaat!!",
            "avatar": "/static/img/blank_avatar.jpg",
            ...
            "current": {
                  "country": "Argentina",
                  "lat": "0E-9",
                  "lon": "0E-9",
                  "name": "Buenos Aires",
                  "region": "Bs As"
            },
            "education": [
                {
                  "degree": "Master of Lords",
                  "institution": "University of Reading"
                },
                {
                  "degree": "Master in Chemistry",
                  "institution": "University of Waterloo"
                }
            ],
            ...
            "instantMessages": [
                {
                  "imUsername": "zek.skype",
                  "instantMessage": "Skype"
                }
              ],
              "interestedIn": [
                {
                  "gender": "Female"
                }
            ],
            "languages": [
                {
                  "level": "intermediate",
                  "name": "english"
                },
                {
                  "level": "expert",
                  "name": "spanish"
                },
                {
                  "level": "beginner",
                  "name": "german"
                }
            ],
            ...
            "socialNetworks": [
                {
                  "snUsername": "lola.facebook",
                  "socialNetwork": "Facebook"
                }
            ],
            "sports": "swimming",
            "user": "/api/v1/accounts/2"
          },
          "msg":"Profile retrieved successfully.",
          "status":true
      }
   * NO
     * 403 FORBIDDEN {"code": 413, "msg": "Error: operation not allowed", "status": false}

### Update my profile (Eze):
 * Request:
    /PUT profiles/me/
    {"X-Auth-Token":"ada787d3684123f27382f53ef7485d42d95ef9aeede39e63de4bb81de3e91df61c2b66af9de50145"}
    {
      "age": 23,
      ...
    }

 * Response:
   * OK
     * 202 Accepted {"code": 200, "msg": "Your profile has been successfully updated.", "status": true}
   * NO
     * 403 FORBIDDEN {"code": 413, "msg": "Error: anonymous users have no profile.", "status": false}
     * 200 OK {"code": 400, "errors": {"emails": ["Enter a valid e-mail address."]}, "msg": "Error in some fields.", "status": false}

### View another profile (Eze):
 * Request:
    /GET profiles/17/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * OK
     * 200 OK 
      {
          "code":200,
          "data": {
            "age":13,
            "allAboutYou": "say whaaaaat!!",
            ...
            "user": "/api/v1/accounts/2"
          },
          "msg":"Profile retrieved successfully.",
          "status":true
      }
          
   * NO
     * 403 FORBIDDEN {"code": 413, "msg": "Error: operation not allowed", "status": false}


### Upload image (Joan) (W8 Sergi):

### Crop image (Joan) (W8 Sergi):

### View my accommodations (Eze):
 * Request:
    GET /profiles/me/accomodations/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * OK
     * 200 OK
        {
          "code": 200,
          "data": [
            {
              "name": "my accomodation in Buenos Aires",
              "uri": "/api/v1/accomodations/97"
            },
            {
              "name": "my accomodation in Madrid",
              "uri": "/api/v1/accomodations/96"
            }
          ],
          "msg": "Accommodations retrieved successfully.",
          "status": true
        }
   * NO 
     * 200 OK {"code": 413, "msg": "Unauthorized", "status": false}

### View another user's accommodations (Eze):
 * Request:
    GET /profiles/2/accomodations/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * OK
     * 200 OK
        {
          "code": 200,
          "data": [
            {
              "name": "my accomodation in Buenos Aires",
              "uri": "/api/v1/accomodations/97"
            },
            {
              "name": "my accomodation in Madrid",
              "uri": "/api/v1/accomodations/96"
            }
          ],
          "msg": "Accommodations retrieved successfully.",
          "status": true
        }
   * NO 
     * 200 OK {"code": 413, "msg": "Unauthorized", "status": false}

### View one of my accommodations (Eze):
 * Request:
    GET /profiles/me/accomodations/20
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * 200 OK
      {
        "code": 200,
        "data": {
          "about": "",
          "additionalInformation": "",
          "address": "",
          "bestDays": "A",
          "blankets": false,
          "bus": false,
          "capacity": "2",
          "city": {
            "city": "Buenos Aires",
            "country": "Argentina",
            "region": "Bs As"
          },
          ...
        },
        "msg": "Accommodation retrieved successfully.",
        "status": true
      }
   * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}

### View an accommodation of another user (Eze):
 * Request:
    GET /profiles/17/accomodations/20
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * 200 OK
      {
        "code": 200,
        "data": {
          "about": "",
          "additionalInformation": "",
          "address": "",
          "bestDays": "A",
          "blankets": false,
          "bus": false,
          "capacity": "2",
          "city": {
            "city": "Madrid",
            "country": "Spain",
            "region": "Madrid"
          },
          ...
        },
        "msg": "Accommodation retrieved successfully.",
        "status": true
      }
   * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}
     * 200 OK {"code": 413, "msg":"Error: Wing not found for that user.", "status": false}

### Create Accommodation (Eze):
 * Request:
    POST /profiles/me/accomodations/
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
    {
      "about": "",
      "additionalInformation": "",
      "address": "",
      ...
      "preferredMale": True,
      "preferredFemale": True,
      ...
    }

 * Response:
   * 201 CREATED {"code": 200, "msg": "Accommodation created successfully.", "status": true}
      
   * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}
     * 200 OK {"code": 400, "errors": {"capacity": ["Select a valid choice. ml is not one of the available choices."]}, "msg": "Error in some fields.", "status": false}

### Update accommodation (Eze):
 * Request:
    PUT /profiles/me/accomodations/20
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
    {
      "about": "",
      "additionalInformation": "",
      "address": "",
      ...
    }

 * Response:
   * 202 ACCEPTED 
      {"code" : 200, "status" : True, "msg" : "Accommodation updated successfully."}
      
   * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}
     * 200 OK {"code": 400, "errors": {"capacity": ["Select a valid choice. ml is not one of the available choices."]}, "msg": "Error in some fields.", "status": false}
     * 200 OK {"code": 413, "msg":"Error: Wing not found for that user.", "status": false}

### Delete accommodation (Eze):
 * Request:
    DELETE /profiles/me/accomodations/20
    {"X-AUTH-TOKEN":"c442e716a18f780212b378810b9cd52b4e3f1774ba79dd19b33a30d3b0efcc032b3669e3da30658c"} 
 * Response:
   * 200 OK 
      {"code": 200, "status": True, "msg":"Accommodation deleted successfully."}
      
   * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}
     * 200 OK {"code": 413, "msg":"Error: Wing not found for that user.", "status": false}

### Search wings (Ezequiel):
  * Request:
    GET /profiles/?wings=Buenos%20Aires&startDate=12-21-2012&endDate=12-26-2012&capacity=4&startAge=20&endAge=23&language=english&gender=Male&type=host&page=1
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}
    
  *Response:
    * 200 OK
      {
        "code": 200,
        "data": 
          {
              "count": 56,
              "profiles": 
              [
                      {
                        "age": 13,
                        "allAboutYou": "",
                        "avatar": "/static/img/blank_avatar.jpg",
                        "current": {
                          "country": "Argentina",
                          "name": "Buenos Aires",
                          "region": "Bs As"
                        },
                        "firstName": "Kim",
                        "languages": [
                          {
                            "level": "intermediate",
                            "name": "english"
                          },
                          {
                            "level": "expert",
                            "name": "spanish"
                          },
                          {
                            "level": "beginner",
                            "name": "german"
                          }
                        ],
                        "lastLogin": "Mon Oct 29 17:01:49 2012",
                        "lastName": "Lorelei",
                        "numFriends": 0,
                        "numReferences": 0,
                        "occupation": "tocar los huevos",
                        "pending": "Pending",
                        "tasaRespuestas": 0,
                        "user": "/api/v1/accounts/2",
                        "verified": true
                      },
                      ...
              ]
          },
        "msg": "Profiles retrieved successfully.",
        "status": true
      }

    * NO 
     * 200 OK {"code": 413, "msg":"Sorry: no results on that page.", "status": false}

    Notes:
      - "X-Auth-Token" is optional: if one valid is provided, the first names, last names and avatars will be the originals; otherwise, they will be faked (blurred)
      - "capacity", "startAge", "endAge", "language" and "type" parameters will always be passed in the uri, the rest are optional
      - "startDate" and "endDate" are in format yyyy-mm-dd
      - "type" must be either "host" or "applicant"

### List languages (Ezequiel):
  * Request:
    GET /languages

  *Response:
    * 200 OK
      {
        "code": 200,
        "data": [
          {
            "name": "english"
          },
          {
            "name": "spanish"
          },
          {
            "name": "german"
          },
          {
            "name": "french"
          }
        ],
        "msg": "Languages retrieved successfully.",
        "status": true
      }

### View my friends (Ezequiel):
  * Request:
    GET /profiles/me/relationships/?status=pendings
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}

  *Response:
    * 200 OK
      {
        "code": 200,
        "data": [
            {
              "avatar": "/static/img/blank_avatar.jpg",
              "first_name": "Pepe",
              "last_name": "Ramirez",
              "uri": "/api/v1/profiles/25"
            },
            {
              "avatar": "/static/img/blank_avatar.jpg",
              "first_name": "Carmen",
              "last_name": "Sanchez",
              "uri": "/api/v1/profiles/28"
            }
        ],
        "msg": "Friends retrieved successfully.",
        "status": true
      }

    * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}

    Notes:
      - "status" must be either "friends" or "pendings"

### Send Invitation (Ezequiel):
  * Request:
    POST /profiles/me/relationships
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}
    {
      "receiver": "/api/v1/profiles/23"
    }

  *Response:
    * 200 OK
      {
        "code": 200,
        "msg": "Invitation sent. Pending to be accepted.",
        "status": true
      }

    * NO 
     * 403 FORBIDDEN {"code": 413, "msg":"Unauthorized", "status": false}
     * 403 FORBIDDEN {"code": 410, "msg":"Cannot be friend of yourself", "status": false}
     * 403 FORBIDDEN {"code": 410, "msg":"The relationship already exists.", "status": false}

### Accept/reject invitation (Ezequiel):
  * Request:
    PUT /profiles/me/relationships/<id_profile>
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}
    {
      "type": "Accepted"
    }

  *Response:
    * 200 OK
      {
        "code": 200,
        "msg": "The invitation has been accepted.",
        "status": true
      }

    * NO 
     * 403 FORBIDDEN {"code": 413, "msg":"Unauthorized", "status": false}
     * 403 FORBIDDEN {"code": 410, "msg":"That friendship doesn't exist.", "status": false}

  Notes:
    - "type" must be either "Accepted" or "Rejected"

### Leave friend (Ezequiel):
  * Request:
    DELETE /profiles/me/relationships/<id_profile>
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}

  *Response:
    * 200 OK
      {
        "code": 200,
        "msg": "You are not friend of that user anymore.",
        "status": true
      }

    * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}
     * 200 OK {"code": 410, "msg":"That friendship doesn't exist.", "status": false}

### Add reference (Ezequiel):
  * Request:
    POST /profiles/<profile_id>/references/
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}
    {
      "title": "This guy is awesome",
      "text": "I had really fun with him, he brought me to the Ramblas, the Cathedral and Paseo Colon :-)",
      "punctuation": "Positive"
    }

  *Response:
    * 200 OK
      {
        "code": 200,
        "msg": "Your reference has been posted.",
        "status": true
      }

    * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}

    Notes:
      - "punctuation" must be either "Positive", "Negative" or "Neutral"

### View another user's references (Ezequiel):
  * Request:
    GET /profiles/<profile_id>/references/
    {"X-Auth-Token":"c1a41e16465376b099c31d8b84dfa4ba78a89d28692f4cebb2b7fdbe676b3ca815973bb9a8834511"}

  *Response:
    * 200 OK
      {
        "code": 200,
        "data": [
          {
            "title": "This guy is awesome",
            "text": "I had really fun with him, he brought me to the Ramblas, the Cathedral and Paseo Colon :-)",
            "punctuation": "Positive"
          },
          {
            "title": "This guy is mean!",
            "text": "This guy is a pervert :-(",
            "punctuation": "Negative"
          },
          {
            "title": "This guy is regular",
            "text": "The visit was OK but many things were left unvisited :-S",
            "punctuation": "Neutral"
          }
        ]
        "msg": "References retrieved successfully.",
        "status": true
      }

    * NO 
     * 200 OK {"code": 413, "msg":"Unauthorized", "status": false}
