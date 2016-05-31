# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

from unittest import TestCase
from nose.tools import eq_, raises
import mock
from mock import Mock
from requests.exceptions import RequestException
from ricohapi.mstorage.client import MediaStorage

class TestInit(TestCase):
    def test_ok(self):
        aclient = Mock()
        mstorage = MediaStorage(aclient)
        eq_(mstorage._MediaStorage__aclient, aclient)
        eq_(mstorage._MediaStorage__endpoint, 'https://mss.ricohapi.com/v1/media')

class TestConnect(TestCase):
    def test_ok(self):
        aclient = Mock()
        mstorage = MediaStorage(aclient)
        mstorage.connect()
        aclient.session.assert_called_once_with('https://ucs.ricoh.com/scope/api/udc2')

class TestMethodOk(TestCase):
    def setUp(self):
        self.aclient = Mock()
        self.aclient.get_access_token = Mock(return_value='atoken')
        self.mstorage = MediaStorage(self.aclient)
        self.mstorage.connect()

    @mock.patch('requests.post')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_upload_ok(self, opn, req):
        opn.side_effect = mock.mock_open()
        opn.read_data = b'readdata'
        req.return_value.text = '{"a": "b"}'
        ret = self.mstorage.upload('path.jpg')
        opn.assert_called_once_with('path.jpg', 'rb')
        headers = {'Authorization': 'Bearer atoken', 'Content-Type': 'image/jpeg'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media', headers=headers, data=opn())
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.get')
    def test_download_ok(self, req):
        req.return_value.content = b'data'
        ret = self.mstorage.download('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media/id1/content', headers=headers, stream=False)
        eq_(ret, b'data')

    @mock.patch('requests.get')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_download_to_ok(self, opn, req):
        opn.side_effect = mock.mock_open()
        req.return_value.iter_content = Mock(return_value=['data'])
        ret = self.mstorage.download_to('id1', 'path.jpg')
        req.return_value.iter_content.assert_called_once_with(chunk_size=1024)
        opn.assert_called_once_with('path.jpg', 'wb')
        opn().write.assert_called_once_with('data')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media/id1/content', headers=headers, stream=True)
        eq_(ret, None)

    @mock.patch('requests.delete')
    def test_delete_ok(self, req):
        params = {'limit': 10}
        ret = self.mstorage.delete('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media/id1', headers=headers)
        eq_(ret, None)

    @mock.patch('requests.get')
    def test_info_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.info('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media/id1', headers=headers, params=None)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.get')
    def test_meta_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.meta('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media/id1/meta', headers=headers, params=None)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.get')
    def test_list_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.list()
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media', headers=headers, params=None)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.get')
    def test_list_params_ok(self, req):
        req.return_value.text='{"a": "b"}'
        params = {'limit': 10}
        ret = self.mstorage.list(params)
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('https://mss.ricohapi.com/v1/media', headers=headers, params=params)
        eq_(ret, {'a': 'b'})

class TestMethodError(TestCase):
    def setUp(self):
        self.aclient = Mock()
        self.aclient.get_access_token = Mock(return_value='atoken')
        self.mstorage = MediaStorage(self.aclient)
        self.mstorage.connect()

    @raises(ValueError)
    @mock.patch('requests.post')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_upload_json_error(self, opn, req):
        opn.side_effect = mock.mock_open()
        req.return_value.text = 'not json'
        ret = self.mstorage.upload('path.jpg')

    @raises(RequestException)
    @mock.patch('requests.post')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_upload_req_error(self, opn, req):
        req.side_effect = RequestException
        ret = self.mstorage.upload('path.jpg')

    @raises(RequestException)
    @mock.patch('requests.get')
    def test_download_req_error(self, req):
        req.side_effect = RequestException
        ret = self.mstorage.download('id1')

    @raises(RequestException)
    @mock.patch('requests.get')
    def test_download_to_req_error(self, req):
        req.side_effect = RequestException
        ret = self.mstorage.download_to('id1', 'path.jpg')

    @raises(Exception)
    @mock.patch('requests.get')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_download_to_error(self, opn, req):
        opn.side_effect = Exception
        ret = self.mstorage.download_to('id1', 'path.jpg')

    @raises(RequestException)
    @mock.patch('requests.get')
    def test_delete_req_error(self, req):
        req.side_effect = RequestException
        ret = self.mstorage.delete('id1')

    @raises(RequestException)
    @mock.patch('requests.get')
    def test_info_req_error(self, req):
        req.side_effect = RequestException
        ret = self.mstorage.info('id1')

    @raises(ValueError)
    @mock.patch('requests.get')
    def test_info_json_error(self, req):
        req.return_value.text = 'not json'
        ret = self.mstorage.info('id1')

    @raises(RequestException)
    @mock.patch('requests.get')
    def test_meta_req_error(self, req):
        req.side_effect = RequestException
        ret = self.mstorage.meta('id1')

    @raises(ValueError)
    @mock.patch('requests.get')
    def test_info_meta_error(self, req):
        req.return_value.text = 'not json'
        ret = self.mstorage.meta('id1')

    @raises(RequestException)
    @mock.patch('requests.get')
    def test_list_req_error(self, req):
        req.side_effect = RequestException
        ret = self.mstorage.list('id1')

    @raises(ValueError)
    @mock.patch('requests.get')
    def test_info_list_error(self, req):
        req.return_value.text = 'not json'
        ret = self.mstorage.list('id1')
