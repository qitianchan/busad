# -*- coding: utf-8 -*-
import requests
import json
data = {
    'district_name': 'XXDDD'
}

# r = requests.delete('http://localhost:5000/api/districts/5', auth=('chan', '000000'))
# r = requests.post('http://localhost:5000/api/districts', json=data, auth=('chan', '000000'))
r = requests.put('http://localhost:5000/api/districts/5', json=data, auth=('chan', '000000'))
print r.status_code
print r.headers['content-type']
print r.text
print r.json()
