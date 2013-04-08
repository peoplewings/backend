from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket            
from django.conf import settings
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
import os

class S3Custom(object):
    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
    k = Key(b)

    def upload_file(self, ruta, prefix):
        try:           
            self.k.key = '%s/%s' % (prefix, os.path.split(ruta)[-1])
            self.k.set_contents_from_filename(ruta)
            self.k.make_public()
        except Exception, e:
            print e
        return '%s%s' % (settings.S3_URL, self.k.key)

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

    def copy(self, srcBucketName, dstBucketName, key):
        srcBucket = self.conn.get_bucket(srcBucketName);
        dstBucket = self.conn.get_bucket(dstBucketName);
        self.k.key = key
        dstBucket.copy_key(k.key, srcBucketName, k.key)
