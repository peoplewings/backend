max_500_char = 500
max_short_len = 20
max_medium_len = 50
max_long_len = 250

PW_STATE_CHOICES = (
    ('Y', 'Yes'),
    ('N', 'No'),
    ('M', 'Maybe'),
    ('T', 'Traveling'),
    ('C', 'Coffee or Drink'),
    ('W', 'By wing'),
)
PW_STATE_CHOICES_KEYS, PW_STATE_CHOICES_VALUES  = zip(*PW_STATE_CHOICES)

SHOW_BIRTHDAY_CHOICES = (
    ('F', 'My full birthday'),
    ('P', 'Only month & day'),
    ('N', 'Don\'t show'),
)
SHOW_BIRTHDAY_CHOICES_KEYS, SHOW_BIRTHDAY_CHOICES_VALUES  = zip(*SHOW_BIRTHDAY_CHOICES)

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)
GENDER_CHOICES_KEYS, GENDER_CHOICES_VALUES  = zip(*GENDER_CHOICES)

CIVIL_STATE_CHOICES = (
    ('','Empty'),
    ('SI', 'Single'),
    ('EN', 'Engaged'),
    ('MA', 'Married'),
    ('WI', 'Widowed'),
    ('IR', 'In a relationship'),
    ('IO', 'In an open relationship'),
    ('IC', 'It\'s complicated'),
    ('DI', 'Divorced'),
    ('SE', 'Separated'),
)
CIVIL_STATE_CHOICES_KEYS, CIVIL_STATE_CHOICES_VALUES  = zip(*CIVIL_STATE_CHOICES)

LANGUAGES_LEVEL_CHOICES = (
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Expert', 'Expert'),
)
LANGUAGES_LEVEL_CHOICES_KEYS, LANGUAGES_LEVEL_CHOICES_VALUES  = zip(*LANGUAGES_LEVEL_CHOICES)

PRIVACY_CHOICES = (
    ('M', 'Only me'),
    ('F', 'Friends'),
    ('E', 'Everybody'),
)


