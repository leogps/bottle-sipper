import gzip
from io import BytesIO


def apply_gzip(request, response, uncompressed_response):
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if 'gzip' in accept_encoding:
        # Compress the response data
        gzip_buffer = BytesIO()
        with gzip.GzipFile(mode='wb', compresslevel=6, fileobj=gzip_buffer) as f:
            f.write(uncompressed_response.encode('utf-8'))

        compressed_data = gzip_buffer.getvalue()

        # Add the 'Content-Encoding' header to indicate compression
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(compressed_data)
        return compressed_data
    return uncompressed_response
