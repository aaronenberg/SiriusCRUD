from io import BytesIO
import os

from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File
from django.core.files import temp as tempfile


class FileWithDirectory(File):
    def __init__(self, file, name=None):
        super().__init__(file, name)
        directory_name = os.path.dirname(name)
        has_directory = len(directory_name) != 0
        if has_directory:
            self.directory_name = name


class UploadedFileWithDirectory(FileWithDirectory, UploadedFile):

    def __init__(self, file=None, name=None, content_type=None, size=None, charset=None, content_type_extra=None):
        super().__init__(file, name)
        self.size = size
        self.content_type = content_type
        self.charset = charset
        self.content_type_extra = content_type_extra

    def _get_directory_name(self):
        return self._directory_name

    def _set_directory_name(self, name):
        if name is not None:
            directory_name = os.path.dirname(name)

        self._directory_name = directory_name

    directory_name = property(_get_directory_name, _set_directory_name)


class TemporaryUploadedFileWithDirectory(UploadedFileWithDirectory):

    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        _, ext = os.path.splitext(name)
        file = tempfile.NamedTemporaryFile(suffix='.upload' + ext, dir=settings.FILE_UPLOAD_TEMP_DIR)
        super().__init__(file, name, content_type, size, charset, content_type_extra)

    def temporary_file_path(self):
        """Return the full path of this file."""
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except FileNotFoundError:
            # The file was moved or deleted before the tempfile could unlink
            # it. Still sets self.file.close_called and calls
            # self.file.file.close() before the exception.
            pass


class InMemoryUploadedFileWithDirectory(UploadedFileWithDirectory):

    """
    A file uploaded into memory (i.e. stream-to-memory).
    """
    def __init__(self, file, field_name, name, content_type, size, charset, content_type_extra=None):
        super().__init__(file, name, content_type, size, charset, content_type_extra)
        self.field_name = field_name

    def open(self, mode=None):
        self.file.seek(0)
        return self

    def chunks(self, chunk_size=None):
        self.file.seek(0)
        yield self.read()

    def multiple_chunks(self, chunk_size=None):
        # Since it's in memory, we'll never have multiple chunks.
        return False


class TemporaryFileWithDirectoryUploadHandler(FileUploadHandler):

    """
    Use directory name to signal whether or not this handler should be used.
    """
        
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.activated = len(os.path.dirname(self.file_name)) != 0
        if self.activated:
            self.file = TemporaryUploadedFileWithDirectory(
                self.file_name,
                self.content_type,
                0,
                self.charset,
                self.content_type_extra
            )
            raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        if self.activated:
            self.file.write(raw_data)
        else:
            return raw_data

    def file_complete(self, file_size):
        if not self.activated:
            return

        self.file.seek(0)
        self.file.size = file_size
        return self.file


class MemoryFileWithDirectoryUploadHandler(FileUploadHandler):

    """
    File upload handler to stream uploads into memory (used for small files).
    """

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        """
        Use the content_length to signal whether or not this handler should be
        used.
        """
        # Check the content-length header to see if we should
        # If the post is too large, we cannot use the Memory handler.
        self.activated = content_length <= settings.FILE_UPLOAD_MAX_MEMORY_SIZE

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.activated = self.activated and len(os.path.dirname(self.file_name)) != 0
        if self.activated:
            self.file = BytesIO()
            raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        """Add the data to the BytesIO file."""
        if self.activated:
            self.file.write(raw_data)
        else:
            return raw_data

    def file_complete(self, file_size):
        """Return a file object if this handler is activated."""
        if not self.activated:
            return

        self.file.seek(0)
        return InMemoryUploadedFileWithDirectory(
            file=self.file,
            field_name=self.field_name,
            name=self.file_name,
            content_type=self.content_type,
            size=file_size,
            charset=self.charset,
            content_type_extra=self.content_type_extra
        )
