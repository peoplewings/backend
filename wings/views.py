# Create your views here.
from django.contrib.auth.decorators import login_required
from wings.models import Wing
from wings.forms import WingForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def manage_wing_information(request):
    if request.method == 'POST':
        form = WingForm(request.POST or None)
        if form.is_valid():
            #form.save()
            save_wing_info(form.cleaned_data, request.user.get_profile())
            return HttpResponseRedirect('/users/profile/')
    else:
        form = WingForm()
    return render_to_response('people/likes_info.html', {'form': form}, context_instance=RequestContext(request))


def save_wing_info(data, profile):
	w = Wing.objects.create(author=profile, max_pw=3)
