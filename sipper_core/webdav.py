import gzip
import os
import pathlib
import shutil
import urllib.parse
import xml.etree.ElementTree as eT
from io import BytesIO
from bottle import request, response, abort, route

from sipper_core.constants import get_mime_extensions
from sipper_core.dir_cache import Dir, File, DirCache

DAV_NS = 'DAV:'


def get_mime_type(filename) -> str:
    """Determine MIME type of a file."""

    extension = pathlib.Path(filename).suffix
    ext = extension.lower().replace('.', '')

    mime_type_extensions = get_mime_extensions()
    if ext in mime_type_extensions:
        mime_type = mime_type_extensions[ext]
    else:
        mime_type = 'application/octet-stream'

    return mime_type


def formatdate(timeval, localtime=False, usegmt=True):
    """Format date according to RFC 1123."""
    from email.utils import formatdate
    return formatdate(timeval, localtime, usegmt)


class WebDavRoutes:
    def __init__(self, directory, gzip_enabled=False, dir_cache: DirCache = None):
        self.directory = directory
        self.gzip_enabled = gzip_enabled
        self.dir_cache = dir_cache
        self._register()

    def _register(self):
        route('/', method='PROPFIND')(self.propfind)
        route('/<path:path>', method='PROPFIND')(self.propfind)
        route('/', method='PROPPATCH')(self.proppatch)
        route('/<path:path>', method='PROPPATCH')(self.proppatch)
        route('/', method='MKCOL')(self.mkcol)
        route('/<path:path>', method='MKCOL')(self.mkcol)
        route('/', method='DELETE')(self.delete)
        route('/<path:path>', method='DELETE')(self.delete)
        route('/', method='PUT')(self.put)
        route('/<path:path>', method='PUT')(self.put)
        route('/', method='COPY')(self.copy)
        route('/<path:path>', method='COPY')(self.copy)
        route('/', method='MOVE')(self.move)
        route('/<path:path>', method='MOVE')(self.move)

    def propfind(self, path='', depth=None):
        return self._webdav_propfind(path, depth=depth)

    @staticmethod
    def proppatch(path=''):
        response.status = 200
        return ""

    def mkcol(self, path=''):
        full_path = os.path.join(self.directory, path.lstrip('/'))
        os.makedirs(full_path, exist_ok=True)
        response.status = 201
        return ""

    def delete(self, path=''):
        full_path = os.path.join(self.directory, path.lstrip('/'))
        if not os.path.exists(full_path):
            abort(404)
        if os.path.isdir(full_path):
            os.rmdir(full_path)
        else:
            os.remove(full_path)
        response.status = 204
        return ""

    def put(self, path=''):
        full_path = os.path.join(self.directory, path.lstrip('/'))
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(full_path, 'wb') as f:
            f.write(request.body.read())
        response.status = 201
        return ""

    def copy(self, path=''):
        dest_header = request.get_header('Destination')
        if not dest_header:
            abort(400)
        parsed_dest = urllib.parse.urlparse(dest_header)
        dest_path = parsed_dest.path
        full_source = os.path.join(self.directory, path.lstrip('/'))
        full_dest = os.path.join(self.directory, str(dest_path).lstrip('/'))
        if not os.path.exists(full_source):
            abort(404)
        dir_path = os.path.dirname(full_dest)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        shutil.copy2(full_source, full_dest)
        response.status = 204
        return ""

    def move(self, path=''):
        dest_header = request.get_header('Destination')
        if not dest_header:
            abort(400)
        parsed_dest = urllib.parse.urlparse(dest_header)
        dest_path = parsed_dest.path
        full_source = os.path.join(self.directory, path.lstrip('/'))
        full_dest = os.path.join(self.directory, str(dest_path).lstrip('/'))
        if not os.path.exists(full_source):
            abort(404)
        dir_path = os.path.dirname(full_dest)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        shutil.move(full_source, full_dest)
        response.status = 204
        return ""

    @staticmethod
    def _add_resourcetype(parent, is_dir):
        if not is_dir:
            return
        resource_type = eT.SubElement(parent, 'D:resourcetype')
        collection = eT.SubElement(resource_type, 'D:collection')
        collection.set('xmlns:D', DAV_NS)

    @staticmethod
    def _add_displayname(parent, displayname_val):
        elem = eT.SubElement(parent, 'D:displayname')
        elem.text = displayname_val

    @staticmethod
    def _add_getlastmodified(parent, value):
        elem = eT.SubElement(parent, 'D:getlastmodified')
        elem.text = value

    @staticmethod
    def _add_lastmodified(parent, value):
        elem = eT.SubElement(parent, 'D:lastmodified')
        elem.text = value

    @staticmethod
    def _add_getcontentlength(parent, value):
        elem = eT.SubElement(parent, 'D:getcontentlength')
        elem.text = value

    @staticmethod
    def _add_getcontenttype(parent, value):
        elem = eT.SubElement(parent, 'D:getcontenttype')
        elem.text = value

    @staticmethod
    def _add_getetag(parent, value):
        elem = eT.SubElement(parent, 'D:getetag')
        elem.text = value

    def _webdav_propfind(self, path, depth=None):
        full_path = os.path.join(self.directory, path.lstrip('/'))
        if not os.path.exists(full_path):
            abort(404)

        is_dir = os.path.isdir(full_path)

        if depth is None:
            depth_header = request.get_header('Depth')
            if depth_header is not None:
                depth = depth_header

        depth_map = {'0': 0, '1': 1, 'infinity': -1}
        depth_int = depth_map.get(str(depth), -1) if depth is not None else -1

        root = eT.Element('D:multistatus')
        root.set('xmlns:D', DAV_NS)

        if is_dir:
            self._add_dir_to_response(root, full_path, path, depth_int)
        else:
            stat = os.stat(full_path)
            etag_value = f'{int(stat.st_mtime)}-{stat.st_size}'
            self._add_resource_to_response(root, full_path, path, str(depth_int), depth_int, stat, etag_value, False)

        response.status = 207
        response.content_type = 'text/xml; charset=utf-8'
        xml_bytes = eT.tostring(root, encoding='utf-8', xml_declaration=True)

        # Apply gzip compression if enabled and client supports it
        if self.gzip_enabled:
            accept_encoding = request.headers.get('Accept-Encoding', '')
            if 'gzip' in accept_encoding:
                gzip_buffer = BytesIO()
                with gzip.GzipFile(mode='wb', compresslevel=6, fileobj=gzip_buffer) as f:
                    f.write(xml_bytes)
                compressed_data = gzip_buffer.getvalue()
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(compressed_data)
                return compressed_data

        return xml_bytes

    def _add_dir_to_response(self, root, full_path, path, depth_int):
        """Add a directory and its descendants to the XML multistatus element.

        Checks DirCache at each directory node before hitting the filesystem.
        On a cache miss the node is built from disk and stored in the cache.
        Partial hits (e.g. cached_depth=1, request depth=infinity) are handled
        transparently: cached children are reused and each child directory is
        checked in the cache independently during recursive traversal.

        depth_int: 0 = self only, 1 = self + immediate children, -1 = infinity
        """
        norm_path = path if path.startswith('/') else '/' + path
        cached = self.dir_cache.get(norm_path, depth_int) if self.dir_cache else None

        if cached:
            dir_node = cached.node
        else:
            stat = os.stat(full_path)
            dir_node = Dir(
                path=norm_path,
                full_path=full_path,
                stat=stat,
                parent_path=os.path.dirname(norm_path) or '/'
            )

        self._add_resource_to_response(
            root, full_path, path,
            str(depth_int), depth_int,
            dir_node.stat, dir_node.etag_value, True
        )

        if depth_int == 0:
            if self.dir_cache and not cached:
                self.dir_cache.put(norm_path, dir_node, 0)
            return

        if cached and (cached.cached_depth >= 1 or cached.cached_depth == -1):
            children = dir_node.children()
        else:
            children = []
            for child_name in os.listdir(full_path):
                child_full = os.path.join(full_path, child_name)
                child_url = norm_path.rstrip('/') + '/' + child_name
                try:
                    child_stat = os.stat(child_full)
                    child_is_dir = os.path.isdir(child_full)
                except OSError:
                    continue
                if child_is_dir:
                    child_node = Dir(
                        path=child_url,
                        full_path=child_full,
                        stat=child_stat,
                        parent_path=norm_path
                    )
                else:
                    child_node = File(
                        path=child_url,
                        full_path=child_full,
                        stat=child_stat,
                        parent_path=norm_path,
                        mime_type=get_mime_type(child_full)
                    )
                dir_node.add_child(child_node)
                children.append(child_node)

        child_remaining = -1 if depth_int == -1 else depth_int - 1

        for child in children:
            if isinstance(child, Dir):
                self._add_dir_to_response(root, child.full_path, child.path, child_remaining)
            else:
                self._add_resource_to_response(
                    root, child.full_path, child.path,
                    str(child_remaining), child_remaining,
                    child.stat, child.etag_value, False
                )

        if self.dir_cache and not cached:
            self.dir_cache.put(norm_path, dir_node, depth_int)

    def _add_resource_to_response(self, root, full_path, path, depth_str, depth_int, stat_result, etag_value, is_dir):
        """Add a response for the target path/resource."""
        w_response = eT.SubElement(root, 'D:response')

        # D:href
        href = eT.SubElement(w_response, 'D:href')
        href_path = urllib.parse.quote(path)
        href.text = href_path if href_path.startswith("/") else "/{}".format(href_path)

        # D:propstat
        propstat = eT.SubElement(w_response, 'D:propstat')

        # D:prop
        prop = eT.SubElement(propstat, 'D:prop')

        displayname_val = os.path.basename(full_path)
        lastmodified_val = str(int(stat_result.st_mtime))
        getlastmodified_val = formatdate(timeval=stat_result.st_mtime, localtime=False, usegmt=True)
        getcontentlength_val = str(stat_result.st_size) if not is_dir else None
        getcontenttype_val = get_mime_type(full_path) if not is_dir else ''
        getetag_val = '"{}"'.format(etag_value)

        self._add_getlastmodified(prop, getlastmodified_val)
        self._add_resourcetype(prop, is_dir)
        self._add_displayname(prop, displayname_val)
        self._add_lastmodified(prop, lastmodified_val)
        if not is_dir:
            self._add_getcontentlength(prop, getcontentlength_val)
        if not is_dir:
            self._add_getcontenttype(prop, getcontenttype_val)
        if not is_dir:
            self._add_getetag(prop, getetag_val)

        status = eT.SubElement(propstat, 'D:status')
        status.text = 'HTTP/1.1 200 OK'

