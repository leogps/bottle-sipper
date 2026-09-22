import os
import pathlib
import shutil
import urllib.parse
import xml.etree.ElementTree as eT
from bottle import request, response, abort, route

from sipper_core.constants import get_mime_extensions

DAV_NS = 'DAV:'


def get_mime_type(filename):
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
    def __init__(self, directory):
        self.directory = directory
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
        
        stat_result = os.stat(full_path)
        is_dir = os.path.isdir(full_path)
        
        if depth is None:
            depth_header = request.get_header('Depth')
            if depth_header is not None:
                depth = depth_header
        
        depth_map = {'0': 0, '1': 1, 'infinity': -1}
        depth_int = depth_map.get(str(depth), -1) if depth is not None else -1
        depth_str = str(depth_int)
        
        etag_value = f'{int(stat_result.st_mtime)}-{stat_result.st_size}'
        # mime_type = get_mime_type(full_path)
        
        # Build XML response
        root = eT.Element('D:multistatus')
        root.set('xmlns:D', DAV_NS)

        # First, add the target resource
        self._add_resource_to_response(root, full_path, path, depth_str, depth_int, stat_result, etag_value, is_dir)
        
        # If depth is 1 or infinity, also add children
        if is_dir and depth_int >= 1:
            self._add_children_to_response(root, full_path, depth_int, path)

        response.status = 207
        response.content_type = 'text/xml; charset=utf-8'
        return eT.tostring(root, encoding='utf-8', xml_declaration=True)

    def _add_resource_to_response(self, root, full_path, path, depth_str, depth_int, stat_result, etag_value, is_dir):
        """Add a response for the target path/resource."""
        w_response = eT.SubElement(root, 'D:response')

        # D:href
        href = eT.SubElement(w_response, 'D:href')
        href.text = path if path.startswith("/") else "/{}".format(path)

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

    def _add_children_to_response(self, root, full_path, depth_int, parent_path):
        """Add responses for children of a directory up to the specified depth."""
        # Handle special case: root directory (empty path)
        if parent_path == '':
            parent_path = '/'

        dir_path_str = full_path
        dir_basename = os.path.basename(full_path)
        _ = '{}{}'.format(parent_path, dir_basename)
        
        dir_contents = os.listdir(dir_path_str)
        
        for child_name in dir_contents:
            child_full_path = os.path.join(dir_path_str, child_name)
            child_path_str = os.path.join(parent_path, child_name)
            child_stat = os.stat(child_full_path)
            _ = f"{int(child_stat.st_mtime)}-{child_stat.st_size}"
            _ = get_mime_type(child_full_path)
            child_is_dir = os.path.isdir(child_full_path)
            
            # Check if we should include this child based on depth
            if depth_int == 1:
                # Add this immediate child
                child_etag_value = f"{int(child_stat.st_mtime)}-{child_stat.st_size}"
                self._add_resource_to_response(root, child_path_str, child_path_str, "1", 1, child_stat, child_etag_value, child_is_dir)
                # For depth 1, we only process immediate children, don't recurse into directories
            else:  # depth_int == -1 (infinity)
                # Recursively add all descendants
                child_etag_value = f"{int(child_stat.st_mtime)}-{child_stat.st_size}"
                self._add_resource_to_response(root, child_path_str, child_path_str, "infinity", -1, child_stat, child_etag_value, child_is_dir)
                
                if child_is_dir:
                    self._add_children_to_response(root, child_full_path, -1, child_path_str)
