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
    __ENDPOINT = 'https://mss.ricohapi.com/v1'
    __MEDIA_ROOT_PATH = '/media'
    __SEARCH_PATH = '/media/search'
    __MEDIA_PATH = '/media/{mid}'
    __CONTENT_PATH = '/media/{mid}/content'
    __META_PATH = '/media/{mid}/meta'
    __USER_META_PATH = '/media/{mid}/meta/user'
    __SCOPE = AuthClient.SCOPES['MStorage']
    __USER_KEY_RE = re.compile(r'^user\.([A-Za-z0-9_\-]{1,256})$')

    def __init__(self, aclient):
        self.__aclient = aclient

    def __create_headers(self, options=None):
        headers = {
            'Authorization': 'Bearer ' + self.__aclient.get_access_token()
        }
        if options is not None:
            headers.update(options)
        return headers

    def __request(self, method, path, **kwargs):
        url = MediaStorage.__ENDPOINT + path
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
        self.__aclient.session(MediaStorage.__SCOPE)

    def upload(self, save_path):
        """upload media"""
        path = MediaStorage.__MEDIA_ROOT_PATH
        headers = self.__create_headers({
            'Content-Type': 'image/jpeg'
        })
        with open(save_path, 'rb') as payload:
            res = self.__request('post', path, headers=headers, data=payload)
        return MediaStorage.__parse_json(res.text)

    def __download(self, mid, **kwargs):
        path = MediaStorage.__CONTENT_PATH.format(mid=mid)
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
        if params is None:
            ret = self.__get_json(MediaStorage.__MEDIA_ROOT_PATH)
        elif not 'filter' in params:
            ret = self.__get_json(MediaStorage.__MEDIA_ROOT_PATH, params=params)
        else:
            payload = {
                'search_version': '2016-07-08',
                'query': params['filter']
            }
            paging = {}
            if 'after' in params:
                paging['after'] = params['after']
            if 'before' in params:
                paging['before'] = params['before']
            if 'limit' in params:
                paging['limit'] = params['limit']
            if len(paging) != 0:
                payload['paging'] = paging
            res = self.__request('post', MediaStorage.__SEARCH_PATH, data=json.dumps(payload))
            ret = MediaStorage.__parse_json(res.text)
        return ret

    def delete(self, mid):
        """delete media meta"""
        path = MediaStorage.__MEDIA_PATH.format(mid=mid)
        self.__request('delete', path)

    def info(self, mid):
        """get media info"""
        path = MediaStorage.__MEDIA_PATH.format(mid=mid)
        return self.__get_json(path)

    def meta(self, mid, scope=None):
        """get media meta"""
        if scope is None:
            path = MediaStorage.__META_PATH.format(mid=mid)
            ret = self.__get_json(path)
        elif scope in {'exif', 'gpano', 'user'}:
            path = MediaStorage.__META_PATH.format(mid=mid) + '/' + scope
            ret = self.__get_json(path)
        else:
            match = MediaStorage.__USER_KEY_RE.match(scope)
            if match:
                path = MediaStorage.__USER_META_PATH.format(mid=mid) + '/' + match.group(1)
                ret = self.__request('get', path).text
            else:
                raise ValueError('Argument {0} is invalid.'.format(scope))
        return ret

    def add_meta(self, mid, meta):
        """add media meta"""
        max_count = 10
        min_len = 1
        max_len = 1024
        if len(meta) > max_count:
            raise ValueError('Number of meta must be less than or equal to {0}.'.format(max_count))

        base_path = MediaStorage.__USER_META_PATH.format(mid=mid) + '/'
        headers = self.__create_headers({
            'Content-Type': 'text/plain'
        })

        for key, value in meta.items():
            match = MediaStorage.__USER_KEY_RE.match(key)
            if match:
                path = base_path + match.group(1)
            else:
                raise ValueError('Key {0} is invalid.'.format(key))

            data = MediaStorage.__encode_to_utf8_bytes(value)
            if len(data) < min_len or len(data) > max_len:
                raise ValueError('Value bytes length must be {0}-{1}.'.format(min_len, max_len))

            self.__request('put', path, headers=headers, data=data)

    def remove_meta(self, mid, scope):
        """remove media meta"""
        path = MediaStorage.__USER_META_PATH.format(mid=mid)
        if scope != 'user':
            match = MediaStorage.__USER_KEY_RE.match(scope)
            if match:
                path += '/' + match.group(1)
            else:
                raise ValueError('Argument {0} is invalid.'.format(scope))
        self.__request('delete', path)
