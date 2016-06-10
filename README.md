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

### Get metadata of a file

```python
mstorage.meta('<media_id>')
```
