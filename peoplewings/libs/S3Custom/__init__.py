from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket            
from django.conf import settings
import uuid

class S3Custom(object):
    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
    k = Key(b)
    def upload_file(self, ruta):
        #this is where the file will live
        return self.k.set_contents_from_filename('%s%s' % (settings.MEDIA_ROOT, ruta))

    def delete_file(self, ruta):        
        self.k.key = ruta
        self.b.delete_key(self.k)

    def exists_file(self, ruta):          
        self.k.key = ruta
        obj = self.b.get_key(self.k)
        return obj is not None
    
    def length_keys(self, prefix):
        self.k.key = prefix
        obj = self.b.get_all_keys(prefix=prefix)
        return len(obj)
    
    def make_name(self):
        return u'{name}'.format(                 
            name = uuid.uuid4().hex
        )
