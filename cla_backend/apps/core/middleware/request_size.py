from django.http import HttpResponseBadRequest
from django.core.files.uploadhandler import MemoryFileUploadHandler, StopUpload

# Limit to 5MB
MAX_REQUEST_CONTENT_LENGTH_BYTES = 5 * 1024 * 1024

class MaxSizeUploadHandler(MemoryFileUploadHandler):
    """
    Custom file upload handler that enforces a maximum file size limit.

    This handler extends Django's MemoryFileUploadHandler to prevent uploads
    that exceed a specified maximum size. It tracks the total bytes received
    and raises a StopUpload exception if the limit is exceeded.

    Attributes:
        total_bytes (int): Running total of bytes received during upload.

    Methods:
        receive_data_chunk(raw_data, start):
            Processes incoming data chunks and enforces size limits.

    Raises:
        StopUpload: When the uploaded file exceeds MAX_REQUEST_CONTENT_LENGTH_BYTES.

    Example:
        To use this handler, configure it in Django settings:
        
        FILE_UPLOAD_HANDLERS = [
            'path.to.MaxSizeUploadHandler',
        ]
    """

    def __init__(self, *args, **kwargs):
        super(MaxSizeUploadHandler, self).__init__(*args, **kwargs)
        self.total_bytes = 0

    def receive_data_chunk(self, raw_data, start):
        self.total_bytes += len(raw_data)
        if self.total_bytes > MAX_REQUEST_CONTENT_LENGTH_BYTES:
            raise StopUpload(connection_reset=True)
        return raw_data

class RequestSizeMiddleware:
    """
    Django middleware to limit the size of incoming HTTP request payloads.
    This middleware enforces a maximum request body size to prevent denial-of-service
    attacks and excessive memory usage from large payloads.
    Attributes:
        get_response (callable): The next middleware or view in the Django request/response chain.
    Methods:
        __init__(get_response):
            Initialises the middleware with the next callable in the chain.
            Args:
                get_response (callable): The next middleware or view to be called.
        __call__(request):
            Processes each incoming request to validate payload size.
            Checks the Content-Length header against MAX_REQUEST_CONTENT_LENGTH_BYTES.
            For POST, PUT, and PATCH requests, inserts a MaxSizeUploadHandler to handle
            file uploads within size constraints.
            Args:
                request (HttpRequest): The incoming Django HTTP request object.
            Returns:
                HttpResponse: Either the response from the next middleware/view, or an
                             HttpResponseBadRequest (status 413) if payload exceeds limit,
                             or HttpResponseBadRequest (status 400) if Content-Length is invalid.
            Raises:
                Returns HttpResponseBadRequest instead of raising exceptions for:
                - Payloads exceeding MAX_REQUEST_CONTENT_LENGTH_BYTES
                - Invalid Content-Length header values
    """

    def process_request(self, request):
        # Ascertain `Content-Length` header
        length = request.META.get("CONTENT_LENGTH")

        if length:
            try:
                if int(length) > MAX_REQUEST_CONTENT_LENGTH_BYTES:
                    return HttpResponseBadRequest("Payload exceeds {} bytes.".format(MAX_REQUEST_CONTENT_LENGTH_BYTES), status=413)
            except (ValueError, TypeError):
                return HttpResponseBadRequest("Invalid content length")
            
        if request.method in ("POST", "PUT", "PATCH"):
            request.upload_handlers.insert(0, MaxSizeUploadHandler())
