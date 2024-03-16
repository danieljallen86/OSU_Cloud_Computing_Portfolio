from flask import Flask, request, jsonify, make_response, \
    render_template, redirect, session
from google.cloud import datastore
from google.cloud.datastore import key
from google.cloud.datastore_v1.proto.query_pb2 import KindExpression
import constants
from boatload_messages import *
from boatload_util import *
from boatload_jwt import *

app = Flask(__name__)
client = datastore.Client()
app.secret_key = constants.secret_key


@app.route('/')
def index():
    if request.args.get('g_jwt') is None:
        return render_template('welcome.html')
    
    else:
        page_jwt = request.args.get('g_jwt')
        jwt_info = validate_jwt(page_jwt)
        user_name = jwt_info['sub']
        real_name = jwt_info['name']

        create_a_user(user_name, real_name)

        return render_template('userinfo.html',
                                realName = real_name,
                                g_jwt = page_jwt,
                                userName = user_name)


@app.route('/owners')
def get_owner_info():
    if request.args.get('state') is None:
        session['state'] = make_state()
        return redirect(get_access_code_url(session['state']))
    
    elif request.args.get('state') == session['state']:
        # get token
        g_tok = request_token(request.args.get('code'))
        session.pop('state')

        return redirect(f'{constants.app_url}?g_jwt={g_tok}')

    else:
        return redirect(f'{constants.app_url}/owners')

    
@app.route('/users', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def user_actions():
    if request.method == 'GET':
        if mime_type_match(request):
            data, code = all_users()

        else:
            data, code = wrong_mime_type()

    else:
        data, code = bad_verb()

    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


@app.route('/users/<user_id>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def remove_user(user_id):
    if request.method == 'DELETE':            
        user_key = client.key(constants.users, int(user_id))
        user = client.get(key=user_key)
        if user:
            data, code = delete_a_user(user_key)
        
        else:
            data, code = mystery_user()

    else:
        data, code = bad_verb()

    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


@app.route('/boats', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def base_boats():
    sub = None
    if 'Authorization' in request.headers.keys():
        token = request.headers['Authorization'].split(' ')[1]
        g_info = validate_jwt(token)
        if g_info:
            sub = g_info['sub']

    if request.method == 'GET' or request.method == 'POST':
        # request must accept JSON
        if mime_type_match(request):
            # Get all boats (GET) or those belonging to an owner
            if request.method == 'GET':
                data, code = get_all_boats(sub)

            # Create a boat (POST)
            else:
                # if a valid JWT
                if sub:
                    data, code = create_a_boat(request.get_json(), sub)
                
                else:
                    data, code = invald_jwt()
                
        # Does not accept JSON
        else:
            data, code = wrong_mime_type()
    
    # NOT a valid route
    else:
        data, code = bad_verb()

    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


@app.route('/boats/<boat_id>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def specific_boat(boat_id):
    sub = None
    if 'Authorization' in request.headers.keys():
        token = request.headers['Authorization'].split(' ')[1]
        g_info = validate_jwt(token)
        if g_info:
            sub = g_info['sub']

    if request.method == 'POST':
        data, code = bad_verb()

    else:
        if sub:
            # get the boat using the boat_id
            boat_key = client.key(constants.boats, int(boat_id))
            boat = client.get(key=boat_key)

            # if the boat exists
            if boat:
                # if the person is the owner
                if boat['owner'] == sub:
                    if request.method == 'DELETE':
                        data, code = delete_a_boat(boat, boat_key)
                    
                    else:
                        if mime_type_match(request):
                            if request.method == 'GET':
                                data, code = get_a_boat(boat)

                            elif request.method == 'PATCH' or \
                                request.method == 'PUT':
                                data, code = edit_boat(boat, request.get_json())
                    
                        else:
                            data, code = wrong_mime_type()

                # otherwise reject the action
                else:
                    data, code = not_your_boat()

            else:
                data, code = mystery_boat()
    
        else:
            data, code = invald_jwt()

    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


@app.route('/loads', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def base_loads():
    if request.method == 'GET' or request.method == 'POST':
        # request must accept JSON
        if mime_type_match(request):
            # Get all boats (GET) or those belonging to an owner
            if request.method == 'GET':
                data, code = get_all_loads()

            # Create a boat (POST)
            else:
                data, code = create_a_load(request.get_json())
                
        # Does not accept JSON
        else:
            data, code = wrong_mime_type()
    
    # NOT a valid route
    else:
        data, code = bad_verb()
             
    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


@app.route('/loads/<load_id>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def specific_load(load_id):
    if request.method == 'POST':
        data, code = bad_verb()

    else:
        sub = None
        if 'Authorization' in request.headers.keys():
            token = request.headers['Authorization'].split(' ')[1]
            g_info = validate_jwt(token)
            if g_info:
                sub = g_info['sub']

        # get the load using the load_id
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)

        # if the load exists
        if load:
            if request.method == 'DELETE':
                # if the person deleting the load owns the boat
                data, code = delete_a_load(load, load_key)
                
            else:
                if mime_type_match(request):
                    if request.method == 'GET':
                        data, code = get_a_load(load)

                    elif request.method == 'PATCH' or \
                        request.method == 'PUT':
                        data, code = edit_load(load, request.get_json())
                
                else:
                    data, code = wrong_mime_type()

        else:
            data, code = mystery_load()

    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


@app.route('/boats/<boat_id>/loads/<load_id>', 
            methods=['DELETE', 'PUT', 'GET', 'PATCH', 'POST'])
def boats_loads_delete_put(boat_id, load_id):
    sub = None
    if 'Authorization' in request.headers.keys():
        token = request.headers['Authorization'].split(' ')[1]
        g_info = validate_jwt(token)
        if g_info:
            sub = g_info['sub']

    if request.method != 'PUT' and request.method != 'DELETE':
        data, code = bad_verb()

    else:
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)

        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)
        if load and boat:
            if boat['owner'] == sub:
                if request.method == 'PUT':
                    # if the load is on a boat, error
                    if load['carrier']:
                        data, code = only_one_boat()

                    # else add the load to the boat
                    else:
                        data, code = load_a_load(boat, load)

                elif request.method == 'DELETE':
                    # if the load is on a boat
                    if load['carrier']:
                        if load['carrier']['id'] == boat.key.id:
                            data, code = unload_a_load(boat, load)

                        else:
                            data, code = not_this_boat()

                    # load not on a boat to be removed
                    else:
                        data, code = load_not_loaded()
            else:
                data, code = not_your_boat()

        elif boat and not load:
            data, code = mystery_load()

        elif not boat and load:                
            data, code = mystery_boat()

        else:
            data, code = all_mysterious()

    return make_response(jsonify(data), code, {'Content-Type': 'application/json'})


if __name__ == "__main__":
    app.run(host='localhost', port=8080, debug=True)
