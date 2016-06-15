# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

"""
RICOH Media Storage
"""

import json
import requests
from ricohapi.auth.client import AuthClient

class MediaStorage(object):
    """media storage"""

    def __init__(self, aclient):
        self.__aclient = aclient
        self.__endpoint = 'https://mss.ricohapi.com/v1/media'

    @staticmethod
    def __raise_response_error():
        raise ValueError('An invalid response was received from the server.')

    def __get_common_headers(self):
        return {
            'Authorization': 'Bearer ' + self.__aclient.get_access_token()
        }

    def connect(self):
        """connect to server"""
        self.__aclient.session(AuthClient.SCOPES['MStorage'])

    def upload(self, path):
        """upload media"""
        headers = self.__get_common_headers()
        headers['Content-Type'] = 'image/jpeg'
        try:
            with open(path, 'rb') as payload:
                req = requests.post(self.__endpoint, headers=headers, data=payload)
                req.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        try:
            ret = json.loads(req.text)
        except ValueError:
            MediaStorage.__raise_response_error()
        return ret

    def __download(self, mid, stream=False):
        headers = self.__get_common_headers()
        try:
            url = self.__endpoint + '/' + mid +'/content'
            req = requests.get(url, headers=headers, stream=stream)
            req.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        return req

    def download(self, mid):
        """download media"""
        req = self.__download(mid)
        return req.content

    def download_to(self, mid, path):
        """download and save media"""
        req = self.__download(mid, stream=True)
        try:
            with open(path, 'wb') as ofile:
                for chunk in req.iter_content(chunk_size=1024):
                    ofile.write(chunk)
        except Exception:
            raise

    def delete(self, mid):
        """delete media meta"""
        headers = self.__get_common_headers()
        try:
            req = requests.delete(self.__endpoint + '/' + mid, headers=headers)
            req.raise_for_status()
        except requests.exceptions.RequestException:
            raise

    def __get_json(self, url, params=None):
        """get"""
        headers = self.__get_common_headers()
        try:
            req = requests.get(url, headers=headers, params=params)
            req.raise_for_status()
        except requests.exceptions.RequestException:
            raise
        try:
            ret = json.loads(req.text)
        except ValueError:
            MediaStorage.__raise_response_error()
        return ret

    def info(self, mid):
        """get media info"""
        return self.__get_json(self.__endpoint + '/' + mid)

    def meta(self, mid):
        """get media meta"""
        return self.__get_json(self.__endpoint + '/' + mid + '/meta')

    def list(self, params=None):
        """list media"""
        return self.__get_json(self.__endpoint, params)
