# Create your views here.
from dbcontrol.models import *
from operator import itemgetter
import imp
import os

def apply_changes():
	#import pdb; pdb.set_trace()
	scr_list = get_script_list()
	scr_list.sort(key=itemgetter('ordering'), reverse=False)
	for src in scr_list:
		apply_individual_script(src['path'], src['name'])


def get_script_list():
	path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))
	script_list = []
	for root,dirs,files in os.walk(path):
	    for f in files:
	        if f.endswith(".py"):
	            script_list.append({"name": f, "path": os.path.join(root,f), "ordering": f.split('-')[1]})

	return script_list

def apply_individual_script(scr, name):
	script = imp.load_source('*', scr)
	script.main()
	try:
		current = DbControl.objects.get(script_path= name)
		if current.applied is False:
			current.applied = True
			current.save()
	except:
		DbControl.objects.create(script_path = name)



