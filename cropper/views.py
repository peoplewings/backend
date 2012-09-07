from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import simplejson
from django.views.generic.edit import FormView
from django.conf import settings
from cropper.models import Original
from cropper.forms import CroppedForm, OriginalForm
import Image
import os

class UploadView(FormView):
    """
    Upload picture to future cropping
    """
    form_class = OriginalForm
    template_name = 'cropper/upload.html'

    def success(self, request, form, original):
        #print original.__dict__
        response = {'id': original.id, 'image': original.image.path.split('/')[-1], 'width': original.image_width, 'height': original.image_height}
        return json_success_response(response)
        #return redirect(original)

    def form_valid(self, form):
        original = form.save()
        if original.image_width > 800: 
            original.image_width, original.image_height = resize_image(original.image.name, (600, 600))
            original.save()
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
        #resize_image(original.image.name, (600, 600))
        cropped.save()

        return self.success(request  = self.request,
                            form     = form,
                            original = self.get_object(),
                            cropped  = cropped)

    def success(self, request, form, original, cropped):
        """
        Default success crop handler
        """
        return HttpResponse(simplejson.dumps({'image': {
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
        path = os.path.join(settings.MEDIA_ROOT, filename)
        im = Image.open(path)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(path, ext)
        return im.size

def json_success_response(dic):
	return json_response({
                'success': True,
                'data': dic,
                })
def json_response(x):
    from django.utils import simplejson
    return HttpResponse(simplejson.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')