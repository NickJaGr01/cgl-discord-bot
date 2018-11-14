import requests
import os
import json

login_email = os.environ['DATHOST_EMAIL']
login_pass = os.environ['DATHOST_PASSWORD']
rcon_pass = os.environ['RCON_PASSWORD']

def create_server(name, location, map):
    p = {
        'game': 'csgo',
        'location': location,
        'name': name,
        'csgo_settings': {
            'enable_gotv': 'true',
            'game_mode': 'classic_competitive',
            'maps_source': 'mapgroup',
            'mapgroup': 'mg_active',
            'mapgroup_start_map': map,
            'pure_server': 'true',
            'rcon': rcon_pass,
            'slots': 5,
            'tickrate': 128
        }
    }
    r = requests.post('https://dathost.net/api/0.1/game-servers', params=json.dumps(p), auth=(login_email, login_pass))
    print(r.status_code)
    return r.json()

def start_server(id):
    p = {
        'allow_host_reassignment': 'true'
    }
    r = requests.post('https://dathost.net/api/0.1/game-servers/%s/start' % id, auth=(login_email, login_pass), data=p)
    r2 = requests.get('https://dathost.net/api/0.1/game-servers/%s' % id, auth=(login_email, login_pass))
    return r2.json()

def stop_server(id):
    r = requests.post('https://dathost.net/api/0.1/game-servers/%s/stop' % id, auth=(login_email, login_pass))

def change_map(id, map):
    p = {
        'csgo_settings': {
            'mapgroup_start_map': map
        }
    }
    r = requests.put('https://dathost.net/api/0.1/game-servers/%s' % id, auth=(login_email, login_pass), data=p)

def get_console(id, max_lines):
    p = {
        'max_lines': line
    }
    r = requests.get('https://dathost.net/api/0.1/game-servers/%s/console' % id, auth=(login_email, login_pass), data=p)
    return r.text

def put_console(id, line):
    p = {
        'line': line
    }
    r = requests.post('https://dathost.net/api/0.1/game-servers/%s/console' % id, auth=(login_email, login_pass), data=p)
