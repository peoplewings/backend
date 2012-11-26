from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings as django_settings
import settings
from peoplewings.libs.S3Custom import S3Custom
from PIL import Image, ImageFilter, ImageDraw
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
            #Open the image from the ImageField and save the path
            original_path = self.image.path
            fp = open(self.image.path, 'rb')
            im = Image.open(StringIO(fp.read()))
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
            #Delete the original image
            fp.close()
            os.remove(original_path)
            #Save other fields
            self.image_width = im.size[0]
            self.image_height = im.size[1]
        return
                    

class Cropped(models.Model):
    def upload_image(self, filename):
        return u'avatar/%s' % filename

    original = models.ForeignKey(Original, related_name = 'cropped', on_delete = models.SET_NULL, null=True)
    image_big = models.ImageField(upload_to = upload_image, editable = False, null=True)
    image_med = models.ImageField(upload_to = upload_image, editable = False, null=True)
    image_small = models.ImageField(upload_to = upload_image, editable = False, null=True)
    image_med_blur = models.ImageField(upload_to = upload_image, editable = False, null=True)
    x = models.PositiveIntegerField(default = 0)
    y = models.PositiveIntegerField(default = 0)
    w = models.PositiveIntegerField(blank = True, null = True)
    h = models.PositiveIntegerField(blank = True, null = True)

    def cropit(self):
        if self.original is None or self.original.image is None or self.x is None or self.y is None or self.w is None or self.h is None:
            print 'Cannot crop None things'
            self.image_big = None
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
            original_path = self.original.image.path
            fp = open(self.original.image.path, 'rb')
            im = Image.open(StringIO(fp.read()))
            #Crop the image 
            im = im.crop((self.x,self.y,self.x+self.w,self.y+self.h))                   
            #Save the image
            temp_handle = StringIO()
            im.save(temp_handle, PIL_TYPE)
            temp_handle.seek(0)
            #Save image to a SimpleUploadedFile which can be saved into ImageField
            suf = SimpleUploadedFile('crop-%s' % os.path.split(self.original.image.name)[-1], temp_handle.read(), content_type=IMG_TYPE)
            #Save SimpleUploadedFile into image field
            self.image_big.save('%s-big.%s' % (os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)
            self.image_med.save('%s-med.%s' % (os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)
            self.image_small.save('%s-small.%s' % (os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)
            self.image_med_blur.save('%s-blur.%s' % (os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)  
            #Delete the original image and close connection
            fp.close()
            os.remove(original_path)
        return 
   
    def create_thumbs(self, size_big, size_med, size_small):
        if self.image_big is None:
            print 'Cannot resize None things'
        else:
            IMG_TYPE = os.path.splitext(self.image_big.name)[1].strip('.')
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
                self.image_big = None
                return
            #Open the image from the ImageField
            original_path_big = self.image_big.path
            original_path_med = self.image_med.path
            original_path_small = self.image_small.path
            original_path_blur = self.image_med_blur.path
            fp_big = open(self.image_big.path, 'rb')
            fp_med = open(self.image_med.path, 'rb')
            fp_small = open(self.image_small.path, 'rb')
            fp_blur = open(self.image_med_blur.path, 'rb')            
            im_big = Image.open(StringIO(fp_big.read()))
            im_med = Image.open(StringIO(fp_med.read()))
            im_small = Image.open(StringIO(fp_small.read()))
            im_med_blur = Image.open(StringIO(fp_blur.read()))          
            #Resize the image
            im_big.thumbnail(size_big, Image.ANTIALIAS)
            im_med.thumbnail(size_med, Image.ANTIALIAS)
            im_small.thumbnail(size_small, Image.ANTIALIAS)
            im_med_blur.thumbnail(size_med, Image.ANTIALIAS)   
            #Blur the image
            im_med_blur = im_med_blur.convert('RGB')
            im_med_blur = self.pre_blur(size_med, im_med_blur)
            for i in range(10):
                im_med_blur = im_med_blur.filter(ImageFilter.BLUR)
            im_med_blur = self.post_blur(size_med, im_med_blur)           
            #Save the images
            temp_handle_big = StringIO()
            im_big.save(temp_handle_big, PIL_TYPE)
            temp_handle_big.seek(0)

            temp_handle_med = StringIO()
            im_med.save(temp_handle_med, PIL_TYPE)
            temp_handle_med.seek(0)

            temp_handle_small = StringIO()
            im_small.save(temp_handle_small, PIL_TYPE)
            temp_handle_small.seek(0)

            temp_handle_med_blur = StringIO()
            im_med_blur.save(temp_handle_med_blur, PIL_TYPE)
            temp_handle_med_blur.seek(0)
            #Save image to a SimpleUploadedFile which can be saved into ImageField
            suf_big = SimpleUploadedFile('%s' % os.path.split(self.image_big.name)[-1], temp_handle_big.read(), content_type=IMG_TYPE)
            suf_med = SimpleUploadedFile('%s' % os.path.split(self.image_med.name)[-1], temp_handle_med.read(), content_type=IMG_TYPE)
            suf_small = SimpleUploadedFile('%s' % os.path.split(self.image_small.name)[-1], temp_handle_small.read(), content_type=IMG_TYPE)
            suf_med_blur = SimpleUploadedFile('%s' % os.path.split(self.image_med_blur.name)[-1], temp_handle_med_blur.read(), content_type=IMG_TYPE)
            #Save SimpleUploadedFile into image field
            self.image_big.save('%s.%s' % (os.path.splitext(suf_big.name)[0],FILE_EXTENSION), suf_big, save=False)
            self.image_med.save('%s.%s' % (os.path.splitext(suf_med.name)[0],FILE_EXTENSION), suf_med, save=False)
            self.image_small.save('%s.%s' % (os.path.splitext(suf_small.name)[0],FILE_EXTENSION), suf_small, save=False)
            self.image_med_blur.save('%s.%s' % (os.path.splitext(suf_med_blur.name)[0],FILE_EXTENSION), suf_med_blur, save=False)
            #Delete old images and close fps
            fp_big.close()
            fp_med.close()
            fp_small.close()
            fp_blur.close()
            os.remove(original_path_big)
            os.remove(original_path_med)
            os.remove(original_path_small)
            os.remove(original_path_blur)            
        return
    def remove_local(self):
        if self.image_big is not None: os.remove(self.image_big.path)
        if self.image_med is not None: os.remove(self.image_med.path)
        if self.image_small is not None: os.remove(self.image_small.path)
        if self.image_med_blur is not None: os.remove(self.image_med_blur.path)
        return
    def pre_blur(self, size, photo):
        edge = 20
        im_blank = Image.new('RGB',((size[0] + edge*2), (size[1] + edge*2)), (0, 0, 0, 0))
        center_copy = photo.copy()
        im_top = photo.copy()
        im_bot = photo.copy()
        im_right = photo.copy()
        im_left = photo.copy()
        im_top = im_top.crop((0, 0, size[0], edge))
        im_bot = im_top.crop((0, size[1] - edge, size[0], edge))
        im_right = im_top.crop((size[0] - edge, 0, edge, size[1]))
        im_left = im_top.crop((0, 0, edge, size[1]))
        im_blank.paste(center_copy, (edge, edge, size[0] + edge, size[1] + edge))
        return im_blank
    def post_blur(self, size, photo):
        edge = 20
        im = photo.crop((edge,edge,size[0] + edge,size[1] + edge))
        return im 
        
        
