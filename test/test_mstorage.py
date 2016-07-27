# -*- coding: utf-8 -*-
# Copyright (c) 2016 Ricoh Co., Ltd. All Rights Reserved.

import json
from unittest import TestCase
from nose.tools import eq_, raises
import mock
from mock import Mock
from requests.exceptions import RequestException
from ricohapi.mstorage.client import MediaStorage

ENDPOINT = 'https://mss.ricohapi.com/v1'
SCOPE = 'https://ucs.ricoh.com/scope/api/udc2'

class TestInit(TestCase):
    def test_ok(self):
        aclient = Mock()
        mstorage = MediaStorage(aclient)
        eq_(mstorage._MediaStorage__aclient, aclient)

class TestConnect(TestCase):
    def test_ok(self):
        aclient = Mock()
        mstorage = MediaStorage(aclient)
        mstorage.connect()
        aclient.session.assert_called_once_with(SCOPE)

class TestMethodOk(TestCase):
    def setUp(self):
        self.aclient = Mock()
        self.aclient.get_access_token = Mock(return_value='atoken')
        self.mstorage = MediaStorage(self.aclient)
        self.mstorage.connect()

    @mock.patch('requests.request')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_upload_ok(self, opn, req):
        opn.side_effect = mock.mock_open()
        opn.read_data = b'readdata'
        req.return_value.text = '{"a": "b"}'
        ret = self.mstorage.upload('path.jpg')
        opn.assert_called_once_with('path.jpg', 'rb')
        headers = {'Authorization': 'Bearer atoken', 'Content-Type': 'image/jpeg'}
        req.assert_called_once_with('post', ENDPOINT+'/media', headers=headers, data=opn())
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_download_ok(self, req):
        req.return_value.content = b'data'
        ret = self.mstorage.download('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/content', headers=headers)
        eq_(ret, b'data')

    @mock.patch('requests.request')
    @mock.patch('ricohapi.mstorage.client.open')
    def test_download_to_ok(self, opn, req):
        opn.side_effect = mock.mock_open()
        req.return_value.iter_content = Mock(return_value=['data'])
        ret = self.mstorage.download_to('id1', 'path.jpg')
        req.return_value.iter_content.assert_called_once_with(chunk_size=1024)
        opn.assert_called_once_with('path.jpg', 'wb')
        opn().write.assert_called_once_with('data')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/content', headers=headers, stream=True)
        eq_(ret, None)

    @mock.patch('requests.request')
    def test_list_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.list()
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media', headers=headers)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_list_params_ok(self, req):
        req.return_value.text='{"a": "b"}'
        params = {'limit': 10}
        ret = self.mstorage.list(params)
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media', headers=headers, params=params)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_list_search_ok(self, req):
        req.return_value.text='{"a": "b"}'
        query = {'key': 'value'}
        params = {'filter': query}
        ret = self.mstorage.list(params)
        headers = {'Authorization': 'Bearer atoken'}
        expected_data = {
            'search_version': '2016-07-08',
            'query': query
        }
        eq_(req.call_count, 1)
        args = req.call_args[0]
        kwargs = req.call_args[1]
        eq_(len(args), 2)
        eq_(args[0], 'post')
        eq_(args[1], ENDPOINT+'/media/search')
        eq_(len(kwargs), 2)
        eq_(kwargs['headers'], headers)
        eq_(json.loads(kwargs['data']), expected_data)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_list_search_paging_ok(self, req):
        req.return_value.text='{"a": "b"}'
        query = {'key': 'value'}
        params = {'filter': query, 'before': 'b', 'after': 'a', 'limit': 10}
        ret = self.mstorage.list(params)
        headers = {'Authorization': 'Bearer atoken'}
        expected_data = {
            'search_version': '2016-07-08',
            'query': query,
            'paging': {
                'before': 'b',
                'after': 'a',
                'limit': 10
            }
        }
        eq_(req.call_count, 1)
        args = req.call_args[0]
        kwargs = req.call_args[1]
        eq_(len(args), 2)
        eq_(args[0], 'post')
        eq_(args[1], ENDPOINT+'/media/search')
        eq_(len(kwargs), 2)
        eq_(kwargs['headers'], headers)
        eq_(json.loads(kwargs['data']), expected_data)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_delete_ok(self, req):
        ret = self.mstorage.delete('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('delete', ENDPOINT+'/media/id1', headers=headers)
        eq_(ret, None)

    @mock.patch('requests.request')
    def test_info_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.info('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1', headers=headers)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_meta_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.meta('id1')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/meta', headers=headers)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_meta_gpano_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.meta('id1', 'gpano')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/meta/gpano', headers=headers)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_meta_exif_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.meta('id1', 'exif')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/meta/exif', headers=headers)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_meta_user_ok(self, req):
        req.return_value.text='{"a": "b"}'
        ret = self.mstorage.meta('id1', 'user')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/meta/user', headers=headers)
        eq_(ret, {'a': 'b'})

    @mock.patch('requests.request')
    def test_meta_user_scope_ok(self, req):
        req.return_value.text='value'
        ret = self.mstorage.meta('id1', 'user.key')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('get', ENDPOINT+'/media/id1/meta/user/key', headers=headers)
        eq_(ret, 'value')


    @mock.patch('requests.request')
    def test_add_meta_ok(self, req):
        meta = {
            'user._Key-0': b'Value0',
            'user._Key-1': b'Value1',
            'user._Key-2': b'Value2',
            'user._Key-3': b'Value3',
            'user._Key-4': b'Value\xEF\xBC\x94',
            'user._Key-5': b'Value\xEF\xBC\x95',
            'user._Key-6': u'Value6',
            'user._Key-7': u'Value7',
            'user._Key-8': u'Value\uFF18',
            'user._Key-9': u'Value\uFF19',
        }
        self.mstorage.add_meta('id1', meta)
        headers = {'Authorization': 'Bearer atoken', 'Content-Type': 'text/plain'}
        eq_(req.call_count, 10)
        req.assert_has_calls([
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-0', headers=headers, data=b'Value0'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-1', headers=headers, data=b'Value1'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-2', headers=headers, data=b'Value2'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-3', headers=headers, data=b'Value3'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-4', headers=headers, data=b'Value\xEF\xBC\x94'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-5', headers=headers, data=b'Value\xEF\xBC\x95'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-6', headers=headers, data=b'Value6'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-7', headers=headers, data=b'Value7'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-8', headers=headers, data=b'Value\xEF\xBC\x98'),
            mock.call('put', ENDPOINT+'/media/id1/meta/user/_Key-9', headers=headers, data=b'Value\xEF\xBC\x99'),
        ], any_order=True)

    @mock.patch('requests.request')
    def test_remove_meta_user_ok(self, req):
        ret = self.mstorage.remove_meta('id1', 'user')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('delete', ENDPOINT+'/media/id1/meta/user', headers=headers)
        eq_(ret, None)

    @mock.patch('requests.request')
    def test_remove_meta_user_scope_ok(self, req):
        ret = self.mstorage.remove_meta('id1', 'user.key')
        headers = {'Authorization': 'Bearer atoken'}
        req.assert_called_once_with('delete', ENDPOINT+'/media/id1/meta/user/key', headers=headers)
        eq_(ret, None)

class TestMethodError(TestCase):
    def setUp(self):
        self.aclient = Mock()
        self.aclient.get_access_token = Mock(return_value='atoken')
        self.mstorage = MediaStorage(self.aclient)
        self.mstorage.connect()

    @raises(RequestException)
    @mock.patch('requests.request')
    def test_info_req_error(self, req):
        req.side_effect = RequestException
        self.mstorage.info('id1')

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_info_json_error(self, req):
        req.return_value.text = 'not json'
        self.mstorage.info('id1')

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_meta_scope_error(self, req):
        req.return_value.text='{"a": "b"}'
        self.mstorage.meta('id1', 'undefined_scope')

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_add_meta_num_error(self, req):
        meta = {'user.'+str(num):str(num) for num in range(11)}
        self.mstorage.add_meta('id1', meta)

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_add_meta_key_error(self, req):
        meta = {'invalid_key': 'value'}
        self.mstorage.add_meta('id1', meta)

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_add_meta_value_empty_error(self, req):
        meta = {'user.key': ''}
        self.mstorage.add_meta('id1', meta)

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_add_meta_value_over_error(self, req):
        value = b''.join([b'a' for dummy in range(1025)])
        meta = {'user.key': value}
        self.mstorage.add_meta('id1', meta)

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_add_meta_value_type_error(self, req):
        meta = {'user.key': 5}
        self.mstorage.add_meta('id1', meta)

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_add_meta_value_encode_error(self, req):
        meta = {'user.key': b'\x82\xA0'}
        self.mstorage.add_meta('id1', meta)

    @raises(ValueError)
    @mock.patch('requests.request')
    def test_remove_meta_scope_error(self, req):
        self.mstorage.remove_meta('id1', 'invalid_scope')
