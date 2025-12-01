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
        """
        Process incoming data chunks and enforce request size limits.

        This method is called iteratively as chunks of request body data are received.
        It tracks the cumulative size of received data and enforces a maximum content
        length limit to prevent excessive memory usage or denial-of-service attacks.

        Args:
            raw_data (bytes): The chunk of raw data received from the request body.
            start (int): The byte position where this chunk starts in the overall request body.

        Returns:
            bytes: The unmodified raw_data chunk to be processed by subsequent handlers.

        Raises:
            StopUpload: If the cumulative total_bytes exceeds MAX_REQUEST_CONTENT_LENGTH_BYTES,
                        with connection_reset=True to immediately terminate the connection.
        """
        self.total_bytes += len(raw_data)
        if self.total_bytes > MAX_REQUEST_CONTENT_LENGTH_BYTES:
            raise StopUpload(connection_reset=True)
        return raw_data


class RequestSizeMiddleware:
    """
    Middleware to enforce size limits on incoming HTTP request payloads.

    This middleware intercepts incoming requests to validate that the payload size
    does not exceed the configured maximum limit (MAX_REQUEST_CONTENT_LENGTH_BYTES).
    It inspects the Content-Length header and rejects requests that are too large
    before they are fully processed, helping to prevent resource exhaustion attacks
    and ensure system stability.

    For POST, PUT, and PATCH requests, it also inserts a custom upload handler
    (MaxSizeUploadHandler) to monitor and enforce size limits during file uploads.

    Attributes:
        None

    Methods:
        process_request(request): Validates request size and configures upload handlers.

    Example:
        Add to MIDDLEWARE in Django settings:
        
        MIDDLEWARE = [
            ...
            'cla_backend.apps.core.middleware.request_size.RequestSizeMiddleware',
            ...
        ]

    Notes:
        - Requires MAX_REQUEST_CONTENT_LENGTH_BYTES to be defined in settings or module scope
        - Returns HTTP 413 (Payload Too Large) for oversized requests
        - Returns HTTP 400 (Bad Request) for invalid Content-Length headers
    """

    def process_request(self, request):
        """
        Process incoming HTTP request to enforce size limits on request payload.

        This method checks the Content-Length header of incoming requests and validates
        that the payload size does not exceed the maximum allowed size defined by
        MAX_REQUEST_CONTENT_LENGTH_BYTES. For POST, PUT, and PATCH requests, it also
        inserts a custom upload handler to monitor upload sizes.

        Args:
            request: The HttpRequest object containing metadata and content information.

        Returns:
            HttpResponseBadRequest: If the content length exceeds the maximum allowed size
                                   (with status 413) or if the content length header is invalid.
            None: If the request passes validation, allowing normal request processing to continue.

        Raises:
            No exceptions are raised directly; invalid content length values are caught
            and returned as HttpResponseBadRequest.
        """
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
