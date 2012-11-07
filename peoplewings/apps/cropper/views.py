from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import FormView, BaseDetailView
from django.conf import settings
from models import Original
from forms import CroppedForm, OriginalForm
from peoplewings.apps.people.models import UserProfile
from peoplewings.apps.ajax.utils import json_response, json_success_response
import Image
import os
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from urllib import unquote
from peoplewings.libs.S3Custom import S3Custom

class UploadView(FormView):
    """
    Upload picture to future cropping
    """
    form_class = OriginalForm
    template_name = 'cropper/upload.html'

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def success(self, request, form, original):
        #print original.__dict__
        response = {'id': original.id, 'image': unquote(original.image.url).split('?')[0], 'width': original.image_width, 'height': original.image_height}
        return json_success_response(response)
        #return redirect(original)

    def form_valid(self, form):
        s3 = S3Custom()
        #print s3.length_keys('avatar/')
        original = form.save()
        #print s3.length_keys('avatar/')
        if original.image_width > 600: 
            original._resize_image((600, 600))
            #print s3.length_keys('avatar/')
            original.save()
            #print s3.length_keys('avatar/')
        return self.success(self.request, form, original)

    def form_invalid(self, form):
        return json_response({
                'success': False,
                'errors': dict(form.errors.items()),
                })

class CropView(FormView):
    """
    Crop picture and save result into model
    """
    form_class = CroppedForm
    template_name = 'cropper/crop.html'

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CropView, self).dispatch(*args, **kwargs)

    def get_object(self):
        """
        Returns the original image object
        """
        return get_object_or_404(Original, pk=self.kwargs['original_id'])

    def get_initial(self):
        """
        Initial dictionary that passed into form instance arguments
        """
        return {'original': self.get_object()}

    def get_context_data(self, **kwargs):
        """
        Context dictionary that passed into template renderer
        """
        return {
            'form': self.get_form(self.form_class),
            'original': self.get_object(),
            'cropped': None
        }

    def form_valid(self, form):
        cropped = form.save(commit=False)
        cropped.save()
        up = UserProfile.objects.get(pk=self.request.user.get_profile().id)
        up.avatar = settings.STATIC_URL + cropped.image.name
        up.save()
        return self.success(request  = self.request,
                            form     = form,
                            original = self.get_object(),
                            cropped  = cropped)

    def success(self, request, form, original, cropped):
        """
        Default success crop handler
        """
        return HttpResponse(json_success_response({'image': {
                'url'    : cropped.image.url,
                'width'  : cropped.w,
                'height' : cropped.h,
            }}), mimetype='application/x-json') if request.is_ajax() else render(request, 'cropper/crop.html',
            {
                'form'     : form,
                'cropped'  : cropped,
                'original' : original
            })

def resize_image(filename, size):
        ext = filename.rsplit('.', 1)[-1]
        path = os.path.join(settings.STATIC_URL, filename)
        im = Image.open(path)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(path, ext)
        return im.size
