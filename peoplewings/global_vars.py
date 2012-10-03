max_500_char = 500
max_long_len = 200

PW_STATE_CHOICES = (
    ('Y', 'Yes'),
    ('N', 'No'),
    ('M', 'Maybe'),
    ('T', 'Traveling'),
    ('C', 'Coffee or Drink'),
    ('W', 'By wing'),
)

BIRTHDAY_CHOICES = (
    ('F', 'My full birthday'),
    ('P', 'Only month & day'),
    ('N', 'Don\'t show'),
)

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

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

LANGUAGES_LEVEL_CHOICES = (
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Expert', 'Expert'),
)

LANGUAGES_LEVEL_CHOICES_KEYS, LANGUAGES_LEVEL_CHOICES_VALUES  = zip(*LANGUAGES_LEVEL_CHOICES)