from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings as django_settings
import settings

import Image
import os
import uuid

def dimension_validator(image):
    """
    """
    if settings.MAX_WIDTH != 0 and image.width > settings.MAX_WIDTH:
        raise ValidationError, _('Image width greater then allowed. </br><small> Maximum width is: ' + str(settings.MAX_WIDTH) + ".</small>")

    if settings.MAX_HEIGHT != 0 and image.height > settings.MAX_HEIGHT:
        raise ValidationError, _('Image height greater then allowed. </br><small> Maximum height is: ' + str(settings.MAX_HEIGHT) + ".</small>")

    if settings.MIN_WIDTH != 0 and image.width < settings.MIN_WIDTH:
        raise ValidationError, _('Image width is too narrow . </br><small> Minimum width is: ' + str(settings.MIN_WIDTH) + ".</small>")

    if settings.MIN_HEIGHT != 0 and image.height < settings.MIN_HEIGHT:
        raise ValidationError, _('Image height is too short. </br><small> Minimum height is: ' + str(settings.MIN_HEIGHT) + ".</small>")

class Original(models.Model):
    def upload_image(self, filename):
        return u'avatar/{name}.{ext}'.format(            
            name = uuid.uuid4().hex,
            ext  = os.path.splitext(filename)[1].strip('.')
        )

    def __unicode__(self):
        return unicode(self.image)

    @models.permalink
    def get_absolute_url(self):
        return 'cropper_crop', [self.pk]    

    owner = models.ForeignKey('people.UserProfile')
    image = models.ImageField(_('Original image'),
        upload_to    = upload_image,
        width_field  = 'image_width',
        height_field = 'image_height',
        validators   = [dimension_validator])
    image_width = models.PositiveIntegerField(_('Image width'),
        editable = False,
        default = 0)
    image_height = models.PositiveIntegerField(_('Image height'),
        editable = False,
        default = 0)

    def _resize_image(self, size):
        try:
            import urllib2 as urllib
            from PIL import Image            
            from cStringIO import StringIO
            from django.core.files.uploadedfile import SimpleUploadedFile
            from boto.s3.connection import S3Connection
            from boto.s3.key import Key
            from boto.s3.bucket import Bucket            
            from django.conf import settings
            '''Open original photo which we want to resize using PIL's Image object'''
            name_original = self.image.url.split('?')[0].split('/')[-1]
            img_file = urllib.urlopen(self.image.url)
            im = StringIO(img_file.read())
            resized_image = Image.open(im)
            
            '''We use our PIL Image object to create the resized image, which already
            has a thumbnail() convenicne method that constrains proportions.
            Additionally, we use Image.ANTIALIAS to make the image look better.
            Without antialiasing the image pattern artificats may reulst.'''
            resized_image.thumbnail(size, Image.ANTIALIAS)

            '''Save the resized image'''
            temp_handle = StringIO()
            ext = self.image.url.rsplit('.', 1)[-1].split('?')[0]
            resized_image.save(temp_handle, ext)
            temp_handle.seek(0)

            
            ''' Save to the image field'''
            print os.path.split(self.image.name)[-1].split('.')[0]
            print os.path.split(self.image.name)
            suf = SimpleUploadedFile(os.path.split(self.image.name)[-1].split('.')[0], temp_handle.read(), content_type='image/%s' % ext)
            self.image.save('%s.%s' % (suf.name, ext), suf, save=True)
            self.image_width = self.image.width
            self.image_height = self.image.height     
            
            conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
            k = Key(b)           
            k.key = 'avatar/%s' % name_original
            b.delete_key(k)
        except ImportError:
            print 'FUCK YOU'
            pass
            

class Cropped(models.Model):
    def __unicode__(self):
        return u'%s-%sx%s' % (self.original, self.w, self.h)

    def upload_image(self, filename):
        return 'avatar/crop-%s' % filename

    def save(self, *args, **kwargs): #force_insert=False, force_update=False, using=None):
        source = self.original.image.path
        
        target = self.upload_image(os.path.basename(source))

        Image.open(source).crop([
            self.x,             # Left
            self.y,             # Top
            self.x + self.w,    # Right
            self.y + self.h     # Bottom
        ]).save(django_settings.MEDIA_ROOT + os.sep + target)

        self.image = target        
        super(Cropped, self).save(*args, **kwargs)

    original = models.ForeignKey(Original,
        related_name = 'cropped',
        verbose_name = _('Original image'),
		on_delete = models.SET_NULL,
		null=True)
    image = models.ImageField(_('Image'),
        upload_to = upload_image,
        editable  = False)
    x = models.PositiveIntegerField(_('offset X'),
        default = 0)
    y = models.PositiveIntegerField(_('offset Y'),
        default = 0)
    w = models.PositiveIntegerField(_('cropped area width'),
        blank = True,
        null = True)
    h = models.PositiveIntegerField(_('cropped area height'),
        blank = True,
        null = True)

    class Meta:
        verbose_name = _('cropped image')
        verbose_name_plural = _('cropped images')
