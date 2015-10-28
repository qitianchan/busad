# -*- coding: utf-8 -*-
import requests
import json
data = {
    'district_name': 'XXDDD'
}
print len('0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff')
# r = requests.delete('http://localhost:5000/api/districts/5', auth=('chan', '000000'))
# r = requests.post('http://localhost:5000/api/districts', json=data, auth=('chan', '000000'))
r = requests.put('http://localhost:5000/api/districts/5', json=data, token='Basic eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ0NjAzODkwOSwiaWF0IjoxNDQ1OTUyNTA5fQ.eyJpZCI6MX0.oEBMvmywvUs4updcyIYWVGE3G5OHZE2g0QRfFZrve-s')
print r.status_code
print r.headers['content-type']
print r.text
print r.json()
