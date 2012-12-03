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
    form_class = OriginalForm
    template_name = 'cropper/upload.html'

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def success(self, request, form, original, errors=None):
        if original:
            response = {'id': original.id, 'image': '%s%s' % (settings.MEDIA_URL, original.image.url), 'width': original.image_width, 'height': original.image_height}
        else :
            return json_response({'success': False, 'errors': errors})
        return json_success_response(response)

    def form_valid(self, form):
        original = form.save()
        if  original.image_width >= 280 and original.image_height >= 281:
            if original.image_width > 600 or original.image_height > 600:
                original.resize((600, 600))
                if not original.image:
                    return self.success(self.request, form, None, errors = 'Error while uploading the image')
                original.save() 
        else:
            return self.success(self.request, form, None, errors = 'The image is too small')       
        return self.success(self.request, form, original)

    def form_invalid(self, form):
        return json_response({
                'success': False,
                'errors': dict(form.errors.items()),
                })
# NOT USING THIS CLASS. GO TO THE API!!
class CropView(FormView):
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
        cropped = form.save()
        up = UserProfile.objects.get(pk=self.request.user.get_profile().id)
        up.avatar = settings.STATIC_URL + cropped.image.name
        up.save()
        return self.success(request = self.request, form = form, original = self.get_object(), cropped  = cropped)

    def success(self, request, form, original, cropped):
        """
        Default success crop handler
        """
        return HttpResponse(json_success_response({'image': {
                'url'    : unquote(cropped.image.url).split('?')[0],
                'width'  : cropped.w,
                'height' : cropped.h,
            }}), mimetype='application/json') 
            
    def form_invalid(self, form):
        return json_response({
                'success': False,
                'errors': dict(form.errors.items()),
                })

def resize_image(filename, size):
        ext = filename.rsplit('.', 1)[-1]
        path = os.path.join(settings.STATIC_URL, filename)
        im = Image.open(path)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(path, ext)
        return im.size
