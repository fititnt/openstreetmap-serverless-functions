# template/

## python3-http-osm
- [python3-http-osm/](python3-http-osm/)
This is a pached version from https://github.com/openfaas/python-flask-template/tree/master/template/python3-http to deal with binary formats (in our case, Zip output).

See also https://github.com/openfaas/python-flask-template/pull/39 and from https://github.com/openfaas/python-flask-template/blob/master/template/python3-http-debian/index.py

```python
def format_body(res, content_type):
    if content_type == 'application/octet-stream':
        return res['body']
    # (...)
```

> @TODO discuss with upstream to potentially add this