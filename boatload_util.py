from google.api_core.exceptions import DataLoss
from google.cloud import datastore
from flask import request
from datetime import date
import constants
from boatload_messages import *
from boatload_jwt import *

client = datastore.Client()


###########
#  Boats  #
###########
def create_a_boat(req_data, owner):
    if missing_boat_data(req_data):
        data, code = missing_boat_data_response()

    else:
        data, code = new_boat(req_data, owner)

    return data, code


def new_boat(req_data, owner):
    new_boat = datastore.entity.Entity(key=client.key(constants.boats))
    new_boat.update({"name": req_data["name"], 
                     "type": req_data["type"], 
                     "length": req_data["length"],
                     "loads": [], 
                     "owner": owner})
    client.put(new_boat)

    data = new_boat
    data["id"] = new_boat.key.id
    data["self"] = f"{constants.app_url}/boats/{new_boat.key.id}"
    code = 201

    return data, code


def get_a_boat(boat):
    data = boat
    data["id"] = boat.key.id
    data["self"] = f"{constants.app_url}/boats/{boat.key.id}"
    if data['loads']:
        for load in data['loads']:
            load['self'] = f'{constants.app_url}/loads/{load["id"]}'
    code = 200

    return data, code


def edit_boat(boat, req_data):
    if request.method == 'PUT':
        data, code = boat_put(boat, req_data)

    else:
        data, code = boat_patch(boat, req_data)

    return data, code


def boat_put(boat, req_data):
    # clear any attribute not sent
    if 'name' not in req_data.keys():
        req_data['name'] = ''

    if 'type' not in req_data.keys():
        req_data['type'] = ''

    if 'length' not in req_data.keys():
        req_data['length'] = None

    boat['name'] = req_data['name']
    boat['type'] = req_data['type']
    boat['length'] = req_data['length']
    client.put(boat)

    data = boat
    data['id'] = boat.key.id
    data['self'] = f'{constants.app_url}/boats/{boat.key.id}'

    code = 200

    return data, code


def boat_patch(boat, req_data):
    if 'name' in req_data.keys():
        boat['name'] = req_data['name']

    if 'type' in req_data.keys():
        boat['type'] = req_data['type']

    if "length" in req_data.keys():
        boat['length'] = req_data['length']

    client.put(boat)

    data = boat
    data['id'] = boat.key.id
    data['self'] = f'{constants.app_url}/boats/{boat.key.id}'

    code = 200

    return data, code


def delete_a_boat(boat, boat_key):
    for b_load in boat['loads']:
        load_key = client.key(constants.loads, int(b_load['id']))
        load = client.get(load_key)
        load['carrier'] = None
        client.put(load)

    client.delete(boat_key)
    return '', 204


def get_all_boats(owner):
    query = client.query(kind=constants.boats)
    query.add_filter('owner','=', owner)
    q_limit = int(request.args.get('limit', constants.page_size))
    q_offset = int(request.args.get('offset', '0'))
    g_iterator = query.fetch(limit=q_limit, offset=q_offset)
    pages = g_iterator.pages
    results = list(next(pages))
    data_len = len(results)

    if g_iterator.next_page_token:
        next_offset = q_offset + q_limit
        next_url = f'{constants.app_url}/boats?limit={q_limit}&offset={next_offset}'
    
    else:
        next_url = None

    for boat in results:
        boat['id'] = boat.key.id
        boat['self'] = f'{constants.app_url}/boats/{boat.key.id}'
        for load in boat['loads']:
            load["self"] = f'{constants.app_url}/loads/{load["id"]}'
    
    data = {'boats': results, 
            'length': data_len}

    if next_url:
        data["next"] = next_url

    code = 200

    return data, code


def missing_boat_data(req_data):
    return 'name' not in req_data.keys() or \
           'type' not in req_data.keys() or \
           'length' not in req_data.keys()


###########
#  Loads  #
###########
def create_a_load(req_data):
    if missing_load_data(req_data):
        data, code = missing_load_data_response()

    else:
        data, code = new_load(req_data)

    return data, code


def missing_load_data(req_data):
    return 'volume' not in req_data.keys() or \
           'content' not in req_data.keys()


def new_load(req_data):
    new_load = datastore.entity.Entity(key=client.key(constants.loads))
    new_load.update({'volume': req_data['volume'], 
                     'carrier': None,
                     'content': req_data['content'], 
                     'creation_date': created_on()})
    client.put(new_load)
    data = new_load
    data['id'] = new_load.key.id
    data['self'] = f'{constants.app_url}/loads/{new_load.key.id}'
    code = 201

    return data, code


def created_on():
    created = str(date.today()).split('-')
    return f'{created[1]}/{created[2]}/{created[0]}'


def get_a_load(load):
    data = load
    data['id'] = load.key.id
    data['self'] = f'{constants.app_url}/loads/{load.key.id}'
    code = 200

    return data, code


def delete_a_load(load, load_key):
    if load['carrier']:
        boat_key = client.key(constants.boats, int(load['carrier']['id']))
        boat = client.get(key=boat_key)
        for b_load in boat['loads']:
            if b_load['id'] == load.key.id:
                boat['loads'].remove(b_load)
        client.put(boat)
    
    client.delete(load_key)
    return '', 204


def get_all_loads():
    query = client.query(kind=constants.loads)
    q_limit = int(request.args.get('limit', constants.page_size))
    q_offset = int(request.args.get('offset', '0'))
    g_iterator = query.fetch(limit=q_limit, offset=q_offset)
    pages = g_iterator.pages
    results = list(next(pages))
    data_len = len(results)

    if g_iterator.next_page_token:
        next_offset = q_offset + q_limit
        next_url = f'{constants.app_url}/loads?limit={q_limit}&offset={next_offset}'
    
    else:
        next_url = None
        
    for load in results:
        load['id'] = load.key.id
        load['self'] = f'{constants.app_url}/loads/{load.key.id}'
        if load['carrier']:
            load['carrier']['self'] = f'{constants.app_url}/boats/{load["carrier"]["id"]}'
    
    data = {'loads': results, 
            'length': data_len}

    if next_url:
        data['next'] = next_url

    code = 200

    return data, code


def edit_load(load, req_data):
    if request.method == 'PUT':
        data, code = load_put(load, req_data)

    else:
        data, code = load_patch(load, req_data)

    return data, code


def load_put(load, req_data):
    # clear any attribute not sent
    if 'volume' not in req_data.keys():
        req_data['volume'] = None

    if 'content' not in req_data.keys():
        req_data['content'] = ''

    load['volume'] = req_data['volume']
    load['content'] = req_data['content']
    client.put(load)

    data = load
    data['id'] = load.key.id
    data['self'] = f'{constants.app_url}/loads/{load.key.id}'

    code = 200

    return data, code


def load_patch(load, req_data):
    if 'volume' in req_data.keys():
        load['volume'] = req_data['volume']

    if "content" in req_data.keys():
        load['content'] = req_data['content']

    client.put(load)

    data = load
    data['id'] = load.key.id
    data['self'] = f'{constants.app_url}/loads/{load.key.id}'

    code = 200

    return data, code


#########
# Users #
#########
def create_a_user(user_name, real_name):
    if not already_user(user_name):
        new_user(user_name, real_name)


def already_user(user_name):
    query = client.query(kind=constants.users)
    users = list(query.fetch())
    for user in users:
        if user['user_name'] == user_name:
            return True


def new_user(user_name, real_name):
    new_user = datastore.entity.Entity(key=client.key(constants.users))
    new_user.update({'user_name': user_name,
                    'real_name': real_name})
    client.put(new_user)
    

def all_users():
    query = client.query(kind=constants.users)
    response = list(query.fetch())
    data_len = len(response)

    for user in response:
        user['id'] = user.key.id

    data = {
        'users': response,
        'length': data_len
        }

    code = 200

    return data, code


def delete_a_user(user_key):
    client.delete(user_key)
    return '', 204


###################
# Boats and Loads #
###################
def load_a_load(boat, load):
    boat['loads'].append({'id': load.key.id})
    client.put(boat)
    load['carrier'] = {'id': boat.key.id}
    client.put(load)
    
    data = ''
    code = 204

    return data, code
    

def unload_a_load(boat, load):
    load['carrier'] = None
    for a_load in boat['loads']:
        if a_load['id'] == load.key.id:
            boat['loads'].remove(a_load)
    client.put(boat)
    client.put(load)
    data = ''
    code = 204

    return data, code

# check the MIME type the client will accept
def mime_type_match(request):
    if request.headers.get('Accept').lower() == 'application/json' or \
            request.headers.get('Accept') == '*/*':
        return True

    else:
        return False
