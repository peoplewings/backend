#! /usr/local/bin/python
from subprocess import call

print 'Doing post pull jobs...'
call(["python", "manage.py", "apply_changes"])

print 'Jobs finished!'
