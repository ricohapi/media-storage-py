# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

"""
RICOH Media Storage
"""

import json
import re
import requests
import six
from ricohapi.auth.client import AuthClient

class MediaStorage(object):
    """media storage"""

    def __init__(self, aclient):
        self.__aclient = aclient
        self.__endpoint = 'https://mss.ricohapi.com/v1'
        self.__re_user_key = re.compile(r'^user\.([A-Za-z0-9_\-]{1,32})$')

    def __create_headers(self, options=None):
        headers = {
            'Authorization': 'Bearer ' + self.__aclient.get_access_token()
        }
        if options is not None:
            headers.update(options)
        return headers

    def __request(self, method, path, **kwargs):
        url = self.__endpoint + path
        if 'headers' not in kwargs:
            kwargs['headers'] = self.__create_headers()
        try:
            res = requests.request(method, url, **kwargs)
            res.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        return res

    @staticmethod
    def __parse_json(text):
        try:
            ret = json.loads(text)
        except ValueError:
            raise ValueError('An invalid response was received from the server.')
        return ret

    def __get_json(self, path, **kwargs):
        res = self.__request('get', path, **kwargs)
        return MediaStorage.__parse_json(res.text)

    @staticmethod
    def __encode_to_utf8_bytes(text):
        error = False
        if isinstance(text, six.text_type): # unicode
            data = text.encode('utf-8')
        elif isinstance(text, six.binary_type): # binary
            data = text
            try:
                data.decode('utf-8', 'strict') # only check (utf-8 binary are allowed)
            except UnicodeError:
                error = True
        else:
            error = True
        if error:
            msg = 'Only unicode string or utf-8 binary are allowed.'
            raise ValueError(msg)
        return data

    def connect(self):
        """connect to server"""
        self.__aclient.session(AuthClient.SCOPES['MStorage'])

    def upload(self, save_path):
        """upload media"""
        path = '/media'
        headers = self.__create_headers({
            'Content-Type': 'image/jpeg'
        })
        with open(save_path, 'rb') as payload:
            res = self.__request('post', path, headers=headers, data=payload)
        return MediaStorage.__parse_json(res.text)

    def __download(self, mid, **kwargs):
        path = '/media/' + mid +'/content'
        res = self.__request('get', path, **kwargs)
        return res

    def download(self, mid):
        """download media"""
        res = self.__download(mid)
        return res.content

    def download_to(self, mid, path):
        """download and save media"""
        res = self.__download(mid, stream=True)
        with open(path, 'wb') as ofile:
            for chunk in res.iter_content(chunk_size=1024):
                ofile.write(chunk)

    def list(self, params=None):
        """list media"""
        path = '/media'
        if params is None:
            ret = self.__get_json(path)
        elif not 'filter' in params:
            ret = self.__get_json(path, params=params)
        else:
            path += '/search'
            data = json.dumps({
                'search_version': '2016-06-01',
                'query': params['filter']
            })
            res = self.__request('post', path, data=data)
            ret = MediaStorage.__parse_json(res.text)
        return ret

    def delete(self, mid):
        """delete media meta"""
        path = '/media/' + mid
        self.__request('delete', path)

    def info(self, mid):
        """get media info"""
        path = '/media/' + mid
        return self.__get_json(path)

    def meta(self, mid, scope=None):
        """get media meta"""
        path = '/media/' + mid + '/meta'
        if scope is None:
            ret = self.__get_json(path)
        elif scope in {'exif', 'gpano', 'user'}:
            path += '/' + scope
            ret = self.__get_json(path)
        else:
            match = self.__re_user_key.match(scope)
            if match:
                path += '/user/' + match.group(1)
                ret = self.__request('get', path).text
            else:
                raise ValueError('Argument ' + str(scope) + ' is invalid.')
        return ret

    def add_meta(self, mid, meta):
        """add media meta"""
        if len(meta) > 10:
            raise ValueError('Number of meta must be less than or equal to 10.')

        base_path = '/media/' + mid + '/meta/user/'
        headers = self.__create_headers({
            'Content-Type': 'text/plain'
        })

        for key, value in meta.items():
            match = self.__re_user_key.match(key)
            if match:
                path = base_path + match.group(1)
            else:
                raise ValueError('Key ' + key + ' is invalid.')

            data = MediaStorage.__encode_to_utf8_bytes(value)
            if len(data) == 0 or len(data) > 1024:
                raise ValueError('Value bytes length must be 1-1024.')

            self.__request('put', path, headers=headers, data=data)

    def remove_meta(self, mid, scope):
        """remove media meta"""
        path = '/media/' + mid + '/meta/user'
        if scope != 'user':
            match = self.__re_user_key.match(scope)
            if match:
                path += '/' + match.group(1)
            else:
                raise ValueError('Argument ' + str(scope) + ' is invalid.')
        self.__request('delete', path)
