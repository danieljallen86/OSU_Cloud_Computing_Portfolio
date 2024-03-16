###########
#  Boats  #
###########
# if missing boat data
def missing_boat_data_response():
    data = {"Error": "The request object is "
                     "missing at least one of the required attributes."}
    code = 400

    return data, code


# invalid boat_id
def mystery_boat():
    data = {"Error": "No boat with this boat_id exists."}
    code = 404

    return data, code


def not_your_boat():
    data = {"Error": "This is not your boat."}
    code = 403

    return data, code


###########
#  Loads  #
###########
def mystery_load():
    data = {"Error": "No load with this load_id exists."}
    code = 404

    return data, code


def missing_load_data_response():
    data = {"Error": "The load must have a volume and content attribute."}
    code = 400

    return data, code


#########
# Users #
#########
def mystery_user():
    data = {'Error': 'No user with that user_id exists.'}
    code = 404

    return data, code


###################
# Boats and Loads #
###################
def missing_data_response():
    data = {"Error": "The request object is "
                     "missing at least one of the required attributes."}
    code = 400

    return data, code


def all_mysterious():
    data = {"Error": "No boat or load with these ids exist."}
    code = 404

    return data, code


def only_one_boat():
    data = {"Error": "Load is already on a boat and cannot be carried by two boats."}
    code = 403

    return data, code


def load_not_loaded():
    data = {"Error": "This load is not on a boat."}
    code = 403

    return data, code


def not_this_boat():
    data = {"Error": "This load is not on this boat."}
    code = 403

    return data, code
    

def invald_jwt():
    data = {"Error": "Invalid or missing JWT."}
    code = 401

    return data, code


# if method not used for that route
def bad_verb():
    data = {"Error": "Verb not recognized for this route."}
    code = 405

    return data, code


# if the MIME type does not match what is being sent
def wrong_mime_type():
    data = {"Error": "Your request must accept 'application/json'"}
    code = 406

    return data, code