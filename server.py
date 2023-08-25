from hashlib import md5
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from schema import CreateUser, CreateAdvertisement, VALIDATION_CLASS
from models import Session, User, Advertisements
from pydantic import ValidationError

app = Flask('app')


class HttpError(Exception):

    def __init__(self, status_code: int, message: dict | list | str):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    error_message = {
        'status': 'error',
        'description': error.message
    }
    response = jsonify(error_message)
    response.status_code = error.status_code
    return response


def get_advertisement(session: Session, advertisement_id: int):
    advertisement = session.get(Advertisements, advertisement_id)
    if advertisement is None:
        raise HttpError(404, message="advertisement not found")
    return advertisement


def get_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, message="user doesn't exist")
    return user


def validate_json(json_data: dict, validation_model: VALIDATION_CLASS):
    try:
        model_obj = validation_model(**json_data).dict()
    except ValidationError as err:
        raise HttpError(400, message=err.errors())
    return model_obj


def hash_password(password: str):
    password_hash = md5(password.encode()).hexdigest()
    return password_hash


class UserView(MethodView):

    def get(self, user_id):
        with Session() as session:
            user = get_user(session, user_id)
            return jsonify({'id': user_id,
                            'username': user.username,
                            'creation_time': user.creation_time.isoformat(),
                            })

    def post(self):
        json_data = validate_json(request.json, CreateUser)
        json_data['password'] = hash_password(json_data['password'])
        with Session() as session:
            user = User(**json_data)
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, f'{json_data["username"]} is busy')
            return jsonify({'id': user.id})


class AdvertisementView(MethodView):

    def get(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_advertisement(session, advertisement_id)
            return jsonify({'title': advertisement.title,
                            'description': advertisement.description,
                            'creation_time': advertisement.creation_time.isoformat(),
                            'user_id': advertisement.user_id,
                            }
                           )

    def post(self):
        json_data = validate_json(request.json, CreateAdvertisement)
        with Session() as session:
            user_name = request.authorization.parameters['username']
            user_obj = session.query(User).filter(User.username == user_name).first()
            json_data['user_id'] = user_obj.id
            advertisement = Advertisements(**json_data)
            session.add(advertisement)
            session.commit()
            return jsonify({'id': advertisement.id,
                            'title': advertisement.title,
                            'description': advertisement.description,
                            'creation_time': advertisement.creation_time.isoformat(),
                            'user_id': advertisement.user_id,
                            })

    def delete(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_advertisement(session, advertisement_id)
            session.delete(advertisement)
            session.commit()
            return jsonify({'status': 'success'})


app.add_url_rule(
    '/user/<int:user_id>',
    view_func=UserView.as_view('get_user'),
    methods=['GET']
)

app.add_url_rule(
    '/user/',
    view_func=UserView.as_view('create_user'),
    methods=['POST']
)

app.add_url_rule(
    '/advertisement/<int:advertisement_id>',
    view_func=AdvertisementView.as_view('get_advertisement'),
    methods=['GET', 'DELETE']
)

app.add_url_rule(
    '/advertisement/',
    view_func=AdvertisementView.as_view('create_advertisement'),
    methods=['POST']
)

if __name__ == '__main__':
    app.run()
