max_500_char = 500
max_short_len = 20
max_medium_len = 50
max_long_len = 250
max_text_msg_len = 1000
max_short_text_len = 200
max_ultra_short_len = 10

PW_STATE_CHOICES = (
    ('Y', 'Yes'),
    ('N', 'No'),
    ('M', 'Maybe'),
    ('T', 'Traveling'),
    ('C', 'Coffee or Drink'),
    ('W', 'By wing'),
)
PW_STATE_CHOICES_KEYS, PW_STATE_CHOICES_VALUES  = zip(*PW_STATE_CHOICES)
WINGS_STATUS = list(PW_STATE_CHOICES)
WINGS_STATUS.pop()
WINGS_STATUS.pop()
WINGS_STATUS.pop()

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

PREFERRED_GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('B', 'Both'),
    ('N', 'None'),
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
CIVIL_STATE_CHOICES_KEYS, CIVIL_STATE_CHOICES_VALUES  = zip(*CIVIL_STATE_CHOICES)

LANGUAGES_LEVEL_CHOICES = (
    ('beginner', 'beginner'),
    ('intermediate', 'intermediate'),
    ('expert', 'expert'),
)
LANGUAGES_LEVEL_CHOICES_KEYS, LANGUAGES_LEVEL_CHOICES_VALUES  = zip(*LANGUAGES_LEVEL_CHOICES)
LANG_LEVEL_CHOICES = [
    ('E', 'expert'),
    ('I', 'intermediate'),
    ('B', 'beginner'),
]

PRIVACY_CHOICES = (
    ('M', 'Only me'),
    ('F', 'Friends'),
    ('E', 'Everybody'),
)

PETS_CHOICES = (
    (0, 'I have pet'),
    (1, 'Guests pets allowed'),
)

TRANSPORT_CHOICES = (
    (0, 'Underground'),
    (1, 'Bus'),
    (2, 'Tram'),
    (3, 'Train'),
    (4, 'Others'),
)

BETTER_DAYS_CHOICES = (
    ('A', 'Any'),
    ('F', 'From Monday to Friday'),
    ('T', 'From Monday to Thursday'),
    ('W', 'Weekend'),
)

WHERE_SLEEPING_CHOICES = (
    ('C', 'Common area'),
    ('P', 'Private area'),
    ('S', 'Shared private area'),
)

SMOKING_CHOICES = (
    ('S', 'I smoke'),
    ('D', 'I don\'t smoke, but guests can smoke here'),
    ('N', 'No smoking allowed'),
)

CAPACITY_OPTIONS=[(str(i), str(i)) for i in range(1, 10)]
CAPACITY_OPTIONS.append(('m', '+9'))
