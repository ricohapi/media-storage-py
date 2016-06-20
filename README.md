# Ricoh Media Storage for Python

Media Storage Python Library for Ricoh API.

## Requirements
You need

- Ricoh API Client Credentials (client_id & client_secret)
- Ricoh ID (user_id & password)

If you don't have them, please register yourself and your client from [THETA Developers Website](http://contest.theta360.com/).

## Install
Befor install, you must install [auth-py](https://github.com/ricohapi/auth-py)

```sh
$ pip install --upgrade git+https://github.com/ricohapi/media-storage-py.git
```

## Uploading a JPEG file
```python
from ricohapi.mstorage.client import MediaStorage
from ricohapi.auth.client import AuthClient

aclient = AuthClient('<your_client_id>', '<your_client_secret>')
aclient.set_resource_owner_creds('<your_user_id>', '<your_password>')

mstorage = MediaStorage(aclient)
mstorage.connect()
print(mstorage.upload('./upload_file_path.jpg'))
```

## SDK API
### AuthClient
```python
aclient = AuthClient('<your_client_id>', '<your_client_secret>')
aclient.set_resource_owner_creds('<your_user_id>', '<your_password>')
```

### Constructor
```python
mstorage = MediaStorage(<AuthClient object>)
```

### Connect to the server
```python
mstorage.connect()
```

### Upload a file
```python
mstorage.upload('./upload_file_path.jpg')
```

### Download a file
```python
mstorage.download_to('<media_id>', './download_file_path.jpg')
```

### Download a file as bytes object
```python
mstorage.download('<media_id>')
```


### List media ids
```python
mstorage.list()

mstorage.list({'limit': 25, 'after': '<cursor-id>'})
```

### Delete a file
```python
mstorage.delete('<media_id>')
```

### Get information of a file
```python
mstorage.info('<media_id>')
```

### Get all metadata of a file
```python
mstorage.meta('<media_id>')
```

### Get specific metadata of a file
```python
mstorage.meta('<media_id>', 'user')

mstorage.meta('<media_id>', 'user.<key>')

mstorage.meta('<media_id>', 'exif')

mstorage.meta('<media_id>', 'gpano')
```

### Add user metadata to a file
Existing metadata value for the same key will be overwritten.
Up to 10 user metadata can be attached to a media data.

```python
mstorage.add_meta('<media_id>', { 'user.<key1>' : '<value1>', 'user.<key2>' : '<value2>', ...})
```


### Remove user metadata from a file
```python
mstorage.remove_meta('<media_id>', 'user.<key>')
```

### Remove all user metadata from a file
```python
mstorage.remove_meta('<media_id>', 'user')
```

### Search media ids by user metadata
return media ids which have all key value pairs

```python
mstorage.list({'filter': { 'meta.user.<key1>' : '<value1>', 'meta.user.<key2>' : '<value2>', ...}})
```
