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
				ordering = f.split('-')[1]
				ordering = ordering.split('.')[0]
				script_list.append({"name": f, "path": os.path.join(root,f), "ordering": ordering})

	return script_list

def apply_individual_script(scr, name):
	try:
		current = DbControl.objects.get(script_path= name)
		if current.applied is False:
			script = imp.load_source('*', scr)
			script.main()
			current.applied = True
			current.save()
	except:
		script = imp.load_source('*', scr)
		script.main()
		DbControl.objects.create(script_path = name, applied=True)

def list_changes():
	scr_list = get_script_list()
	scr_list.sort(key=itemgetter('ordering'), reverse=False)
	for src in scr_list:
		print_individual_script(src['path'], src['name'])

def print_individual_script(scr, name):
	to_print = name
	try:
		current = DbControl.objects.get(script_path= name)
		if current.applied is False:
			to_print = to_print + ' ...... PENDING'
		else:
			to_print = to_print + ' ...... APPLIED'
	except:
		to_print = to_print + ' ...... PENDING'
	print to_print

def one_change(number):
	scr_list = get_script_list()
	#import pdb; pdb.set_trace()
	#[{name=file, path=full path, ordering=order}]
	if number in [str(i['ordering']) for i in scr_list]:
		path, name = [(i['path'], i['name']) for i in scr_list if i['ordering'] == number][0]
		#print path + ' ' + name 
		apply_individual_script(path, name)
		print 'Applied script n %s' % number
	else:
		print 'Could not find the selected script'



