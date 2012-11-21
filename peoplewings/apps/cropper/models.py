from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings as django_settings
import settings
from peoplewings.libs.S3Custom import S3Custom
from PIL import Image
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import uuid

class Original(models.Model):
    def upload_image(self, filename):
        return u'avatar/{name}.{ext}'.format(            
            name = uuid.uuid4().hex,
            ext  = os.path.splitext(filename)[1].strip('.')
        )

    def __unicode__(self):
        return unicode(self.image)

    owner = models.ForeignKey('people.UserProfile')
    image = models.ImageField(upload_to = upload_image, width_field  = 'image_width', height_field = 'image_height')
    image_width = models.PositiveIntegerField(editable = False, default = 0)
    image_height = models.PositiveIntegerField(editable = False, default = 0)  
    
    def resize(self, size):
        if self.image is None or self.image_width is None or self.image_height is None:
            print 'Cannot resize None things'
        else:
            IMG_TYPE = os.path.splitext(self.image.name)[1].strip('.')
            if IMG_TYPE == 'jpeg':
                PIL_TYPE = 'jpeg'
                FILE_EXTENSION = 'jpg'
            elif IMG_TYPE == 'jpg':
                PIL_TYPE = 'jpg'
                FILE_EXTENSION = 'jpg'
            elif IMG_TYPE == 'png':
                PIL_TYPE = 'png'
                FILE_EXTENSION = 'png'
            elif IMG_TYPE == 'gif':
                PIL_TYPE = 'gif'
                FILE_EXTENSION = 'gif'
            else:
                print 'Not a valid format'
                self.image = None
                return
            #Open the image from the ImageField
            self.image.open()
            im = Image.open(StringIO(self.image.read()))
            #Resize the image
            im.thumbnail(size, Image.ANTIALIAS)
            #Save the image
            temp_handle = StringIO()
            im.save(temp_handle, PIL_TYPE)
            temp_handle.seek(0)
            #Save image to a SimpleUploadedFile which can be saved into ImageField
            suf = SimpleUploadedFile(os.path.split(self.image.name)[-1], temp_handle.read(), content_type=IMG_TYPE)
            #Save SimpleUploadedFile into image field
            self.image.save('%s.%s' % (os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)
            #Save other fields
            self.image_width = im.size[0]
            self.image_height = im.size[1]
        return
                    

class Cropped(models.Model):
    def upload_image(self, filename):
        return u'avatar/%s' % filename

    original = models.ForeignKey(Original, related_name = 'cropped', on_delete = models.SET_NULL, null=True)
    image = models.ImageField(upload_to = upload_image, editable = False)
    x = models.PositiveIntegerField(default = 0)
    y = models.PositiveIntegerField(default = 0)
    w = models.PositiveIntegerField(blank = True, null = True)
    h = models.PositiveIntegerField(blank = True, null = True)
    def cropit(self):
        if self.original is None or self.original.image is None or self.x is None or self.y is None or self.w is None or self.h is None:
            print 'Cannot crop None things'
            self.image = None
        else:
            IMG_TYPE = os.path.splitext(self.original.image.name)[1].strip('.')
            if IMG_TYPE == 'jpeg':
                PIL_TYPE = 'jpeg'
                FILE_EXTENSION = 'jpg'
            elif IMG_TYPE == 'jpg':
                PIL_TYPE = 'jpg'
                FILE_EXTENSION = 'jpg'
            elif IMG_TYPE == 'png':
                PIL_TYPE = 'png'
                FILE_EXTENSION = 'png'
            elif IMG_TYPE == 'gif':
                PIL_TYPE = 'gif'
                FILE_EXTENSION = 'gif'
            else:
                print 'Not a valid format'
                self.original.image = None
                return
            #Open the image from the ImageField
            self.original.image.open()
            im = Image.open(StringIO(self.original.image.read()))
            #Crop the image
            im.crop((self.x,self.y,self.x+self.w,self.y+self.h))
            #Save the image
            temp_handle = StringIO()
            im.save(temp_handle, PIL_TYPE)
            temp_handle.seek(0)
            #Save image to a SimpleUploadedFile which can be saved into ImageField
            suf = SimpleUploadedFile('crop-%s' % os.path.split(self.original.image.name)[-1], temp_handle.read(), content_type=IMG_TYPE)
            #Save SimpleUploadedFile into image field
            self.image.save('%s.%s' % (os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)  
        return                                            
