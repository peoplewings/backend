#!/usr/bin/python

import sys
import os

fixtures_path = 'peoplewings/general_fixtures/'
command = 'python manage.py loaddata %s%s.json'
user_list = []
locations_list = []
people_list = ['user', 'locations']
wings_list = ['people']
notifications_list = ['wings', 'people'] 

sys.argv.pop(0)
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

args = sys.argv
def drop_DB():
    os.system('python manage.py flush')

def init(args):
    drop_DB()
    load_fixtures(args)

def load_fixtures(args):
    for i in args:
        try:
            exec 'aux_list = %s_list' % i
            if len(aux_list) > 0:
                #infere
                load_fixtures(aux_list)
                aux_list.pop(0)
                print 'Loading fixture "%s%s.json"' % (fixtures_path, i)
                os.system(command % (fixtures_path, i))
            else:
                print 'Loading fixture "%s%s.json"' % (fixtures_path, i)
                os.system(command % (fixtures_path, i))
        except Exception, e:
            print e
            print '%s is not a valid choice' % i
            raise e

init(args)

