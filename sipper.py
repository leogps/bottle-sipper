#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sipper is a simple, zero-configuration command-line static HTTP server. It is built on bottle:
https://github.com/bottlepy/bottle | https://bottlepy.org/docs/dev/ It aims to provide the same value provided by
http-server tool written in nodejs: https://github.com/http-party/http-server |
https://www.npmjs.com/package/http-server

Copyright (c) 2022-2023, Paul Gundarapu. License: MIT (see LICENSE for details)
"""

import os
import pathlib
from argparse import ArgumentParser
from datetime import datetime
from threading import Thread
from time import sleep

import ifaddr
from bottle import get, run, static_file, request, response, HTTPResponse, SimpleTemplate

from server import SipperWSGIRefServer
from sipper_core.auth import Authentication, BasicAuthentication
from sipper_core.constants import get_icons, get_mime_extensions, YES, get_templates, get_default_template, \
    find_existing_template, \
    get_python_version, \
    APP_NAME, \
    APP_LINK
from sipper_core.common import perms_to_string, sizeof_fmt, handle_shortcut_symbols, build_icons
from sipper_core.html import FileDetails, FileRow, FileColumn, ITag, AnchorHtmlTag


class Sipper(Thread):

    def __init__(self,
                 directory,
                 show_directory_listings=True,
                 auth=Authentication(),
                 use_available_template=get_default_template().name,
                 template_base_dir=None):
        Thread.__init__(self)
        directory = handle_shortcut_symbols(directory)
        self.directory = directory
        self.show_directory_listings = show_directory_listings
        self.authentication = auth
        self.daemon = False
        self.threads = []
        self.servers = []
        if template_base_dir is not None:
            self.template_base_dir = template_base_dir
        else:
            if use_available_template is None:
                use_available_template = get_default_template().name
            existing_template = find_existing_template(use_available_template)
            if existing_template is None:
                raise Exception('template not found: ' + use_available_template + '\nAvailable templates: ' +
                                ', '.join(
                                    i.name
                                    for i in
                                    get_templates()
                                ))
            else:
                self.template_base_dir = existing_template.path

    def get_server_address(self):
        return ':'.join([request.remote_addr, str(self.server_port)])

    def handle_auth(self, req, res):
        header = req.get_header('Authorization')
        if not isinstance(header, str) or not self.authentication.authenticate(header):
            self.authentication.decorate_with_auth_required(res)
            raise res.copy(cls=HTTPResponse)

    def serve(self, url_path=''):
        if self.authentication.enabled:
            self.handle_auth(request, response)
        # print('Requested: %s' % url_path)
        url_path_normalized = url_path.replace('/', '', 1)
        filename = os.path.join(self.directory, url_path_normalized)
        is_dir = os.path.isdir(filename)
        if is_dir:
            return self.handle_dir(filename)

        extension = pathlib.Path(filename).suffix
        ext = extension.lower().replace('.', '')
        mime_type = None
        mime_type_extensions = get_mime_extensions()
        if ext in mime_type_extensions:
            mime_type = mime_type_extensions[ext]
        return static_file(filename=url_path_normalized, root=self.directory, mimetype=mime_type)

    def handle_dir(self, path):
        if os.path.isfile(os.path.join(path, 'index.html')):
            return static_file(filename='index.html', root=path)

        if not self.show_directory_listings:
            return HTTPResponse(status=403, body=None)

        dir_list = sorted(os.listdir(path), key=lambda v: (not os.path.isdir(os.path.join(path, v)), v.upper()))

        rows = []
        col_template_file = self.build_template_file_path('col.tpl')
        link_template_file = self.build_template_file_path('link.tpl')
        itag_template_file = self.build_template_file_path('i.tpl')
        icons = build_icons()
        icons_json = get_icons()
        for f in dir_list:
            file_path = os.path.join(path, f)

            columns = []

            icon = ITag(['icon'])
            icon_style_class = '_blank'
            if os.path.isfile(file_path):
                extension = pathlib.Path(file_path).suffix
                ext = extension.lower().replace('.', '')
                if ext in icons_json:
                    icon_style_class = ext
            file_details_file_icon_base64 = icons_json[icon_style_class]
            icon.add_style_class(''.join(['icon-', icon_style_class]))
            icon_col = FileColumn(name='icon',
                                  value=icon,
                                  col_template_file=col_template_file,
                                  is_itag=True,
                                  itag_template_file=itag_template_file)

            last_modified = os.path.getmtime(file_path)
            modified_date = datetime.fromtimestamp(last_modified).strftime('%d-%b-%Y %H:%M')
            modified_date_col = FileColumn(name='last_modified_date',
                                           value=modified_date,
                                           style_class='',
                                           col_template_file=col_template_file)

            stat_info = os.stat(file_path)

            file_permissions = ''.join(['(', perms_to_string(stat_info, os.path.isdir(file_path)), ')'])
            file_permissions_col = FileColumn(name='file_permissions',
                                              value=file_permissions,
                                              col_template_file=col_template_file)

            if os.path.isfile(file_path):
                file_details_is_dir = False
                size = stat_info.st_size
                size_formatted = sizeof_fmt(size)
                size_col = FileColumn(name='file_size',
                                      value=size_formatted,
                                      style_class='file-size',
                                      col_template_file=col_template_file)
            else:
                file_details_is_dir = True
                size_formatted = ''
                size_col = FileColumn(name='file_size',
                                      value=size_formatted,
                                      style_class='file-size',
                                      col_template_file=col_template_file)

            link_path = '/'.join([path.replace(self.directory, '', 1), f]).replace('//', '/')
            link_path = ('/' + link_path) if not link_path.startswith('/') else link_path
            link = AnchorHtmlTag(link=link_path, link_text=f)
            link_col = FileColumn(name='file_link',
                                  value=link,
                                  style_class='display-name',
                                  col_template_file=col_template_file,
                                  is_link=True,
                                  link_template_file=link_template_file)

            columns.append(icon_col)
            columns.append(file_permissions_col)
            columns.append(modified_date_col)
            columns.append(size_col)
            columns.append(link_col)

            file_details = FileDetails(is_dir=file_details_is_dir,
                                       file_icon_style_class=icon_style_class,
                                       file_icon_base64=file_details_file_icon_base64,
                                       last_modified_date=modified_date,
                                       file_permissions=file_permissions,
                                       file_size=size_formatted,
                                       file_link=link_path,
                                       file_name=f)
            row = FileRow(file_details=file_details, cols=columns)
            rows.append(row)

        html = SimpleTemplate(name=self.build_template_file_path('index.tpl'))
        index_of = path.replace(self.directory, '', 1)

        html_model = {
            'dir': index_of,
            'rows': rows,
            'row_template_file': self.build_template_file_path('row.tpl'),
            'icons': icons,
            'python_version': get_python_version(),
            'app_name': APP_NAME,
            'app_link': APP_LINK,
            'server_address': self.get_server_address()
        }

        html = html.render(**html_model)
        return html

    def build_template_file_path(self, template_file):
        return os.path.join(self.template_base_dir, template_file)

    def _run(self, address, port):
        # print('Serving at http://{}:{}'.format(ip, port))
        server = SipperWSGIRefServer(host=address, port=port)
        self.servers.append(server)
        self.server_port = port
        run(quiet=False, server=server)

    def start_sipping(self, address, port):
        thread = Thread(target=self._run, args=[address, port])
        thread.start()
        self.threads.append(thread)

    def shutdown(self, wait_before_shutdown=0):
        print('Shutting down...')
        sleep(wait_before_shutdown)
        for server in self.servers:
            server.shutdown()


def main():
    pass


if __name__ == "__main__":
    main()

    parser = ArgumentParser()
    parser.add_argument('-d', '--show-dir', default=True, required=False, help='Show directory listings')
    parser.add_argument('-a', '--address', required=False, help='Address for the server, defaults to 0.0.0.0')
    parser.add_argument('-p', '--port', default=8080, required=False, help='Port for the server')
    parser.add_argument('-u', '--username', default=None, required=False, help='Username for basic authentication')
    parser.add_argument('-P', '--password', default=None, required=False, help='Password for basic authentication')
    parser.add_argument('-b', '--template-base-dir', default=None, required=False, help='Template base directory. '
                                                                                        'Takes precedence over '
                                                                                        '--use-available-template '
                                                                                        'option')
    parser.add_argument('-t', '--use-available-template', default=None, required=False, help='Use out-of-the-box '
                                                                                             'templates. '
                                                                                             'Available templates: ' +
                                                                                             ', '.join(
                                                                                                 i.name
                                                                                                 for i in
                                                                                                 get_templates()
                                                                                             ))
    parser.add_argument('directory')

    args = parser.parse_args()
    if not isinstance(args.show_dir, bool):
        args.show_dir = True if (args.show_dir in YES) else False

    authentication = Authentication()
    if args.username is not None or args.password is not None:
        if args.username is None:
            args.username = ''
        if args.password is None:
            args.password = ''
        authentication = BasicAuthentication(enabled=True, username=args.username, password=args.password)

    sipper = Sipper(args.directory, show_directory_listings=args.show_dir, auth=authentication,
                    use_available_template=args.use_available_template,
                    template_base_dir=args.template_base_dir)
    get('<url_path:path>')(sipper.serve)

    # sipper.start('0.0.0.0', args.port)
    if args.address is None:
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            # print("IPs of network adapter " + adapter.nice_name)
            for ip in adapter.ips:
                # print("   %s/%s" % (ip.ip, ip.network_prefix))
                theIp = ip.ip
                if (theIp is None or (not isinstance(theIp, str)) or (ip.is_IPv6 and theIp.find('%') != -1) or (
                        ip.nice_name.startswith('utun') or (ip.nice_name.startswith('bridge')))):
                    continue
                sipper.start_sipping(theIp, args.port)
    else:
        sipper.start_sipping(args.address, args.port)
        pass
