import os
from tempfile import mkstemp, mkdtemp
from shutil import rmtree
from boto.s3.connection import S3Connection
from boto.s3.key import Key

class ZipBackup(object):
    def __init__(self, name):
        self.name = name
        _, self._path = mkstemp()
    
    def __enter__(self):
        return self
        
    def __exit__(self):
        self.close()
        
    def close(self):
        os.remove(self._path)
    
    def include_directory(self, path, preserve_paths=False, name=None):
        path = os.abspath(path)
        with ZipFile(self._path, 'w') as zipfile:
            for base,dirs,files in os.walk(path):
                for file in files:
                    filename = os.path.join(base, file)
                    zipfile.write(filename, 
                                  self._get_filename_for_archive(path, filename, 
                                                                 preserve_paths, 
                                                                 name))
    
    def save_to_s3(self, bucket, access_key, secret_key):
        conn = S3Connection(access_key, secret_key)
        bucket = conn.get_bucket(bucket)
        key = Key(bucket)
        key.key = '%s_%s.zip' % 
            (self.name, datetime.now().strftime("%Y%m%d%H%M%S"))
        key.set_contents_from_filename(zipfile_path)
        
    def _get_filename_for_archive(self, directory, filename, preserve_paths, name):
        if not preserve_paths:
            filename = filename.replace(directory, "")
        if name is not None:
            filename = name + os.sep + filename
        return filename
    
    def include_new_dir(self, name):
        return TemporaryBackupDirectory(name, self)
        
class TemporaryBackupDirectory(object):
    def __init__(self, name, parent):
        self.name = name
        self._dir = mkdtemp()
        self._parent = parent
    
    def __str__():
        return self._dir
    
    def __enter__(self):
        return self
        
    def __exit__(self):
        parent.include_directory(self._dir, preserve_paths=False, 
                                 name=self.name)
        shutil.rmtree(self._dir)

