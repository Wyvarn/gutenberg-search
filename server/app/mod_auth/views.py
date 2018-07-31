from flask import request, jsonify
# from flask_api.exceptions import AuthenticationFailed, NotFound
# from flask_login import login_user, logout_user, login_required, current_user
# from app import db
# from .exceptions import UserAlreadyExists, CredentialsRequired

from . import auth
from .models import UserAccount, UserProfile
from .security_utils import generate_auth_token


@auth.route('/login/', methods=["POST", "GET"])
def login():
    """
    Login view that logs in existing users to the api service
    :return: JSON response with either a success or failure status codes
    """
    if request.method == "GET":
        raise CredentialsRequired()
    else:
        username = request.values.get("username")
        password = request.values.get("password")
        user_account = UserAccount.query.filter_by(username=username).first()

        # check for password validity
        if user_account is not None:
            if user_account.verify_password(password):
                token = generate_auth_token(username, password)
                db.session.commit()
                login_user(user_account)
                return jsonify({
                    "message": 'You have logged in successfully',
                    "response": "Success",
                    'token': token
                })
            else:
                raise AuthenticationFailed()
        else:
            return jsonify({
                "message": "Username {} does not exist".format(username),
                "error": True
            }), 401


@auth.route('/register/', methods=["POST", "GET"])
def register():
    """
    Registration route handling new user addition to the api service
    This will raise an exception if the user already exists in the database
    :raises: UserAlreadyExists exception
    :return: JSON response with more instructions on how to use the API and status code
    """
    if request.method == "GET":
        return jsonify({"message": "Welcome to BucketList Service",
                        "more": "To register make a POST with username and password to /auth/register/"}), 200
    else:
        username = request.values.get("username")
        password = request.values.get("password")
        email = request.values.get("email")
        first_name = request.values.get("first_name")
        last_name = request.values.get("last_name")
        if username and password:
            user_account = UserAccount.query.filter_by(username=username).first()
            if user_account is not None:
                raise UserAlreadyExists()
            else:
                user_profile = UserProfile(first_name=first_name, last_name=last_name,
                                           email=email)
                db.session.add(user_profile)
                db.session.commit()

                user_account = UserAccount(username=username, email=email, password=password,
                                           user_profile_id=user_profile.id)
                db.session.add(user_account)
                db.session.commit()
                login_user(user_account)
                return jsonify({
                    "message": "Registered successfully",
                    "more": "Login using POST to /auth/login/"
                }), 201

    return jsonify({}), 200


@auth.route("/logout/", methods=["GET"])
@login_required
def logout():
    """
    Logout route, handles logging out of users
    :return: JSOn response informing client about status of logging out from service
    """
    user_account = UserAccount.query.filter_by(id=current_user.id).first()

    if user_account:
        # db.session.delete(session)
        logout_user()
        return jsonify({
            "message": "You have logged out successfully"
        })
    else:
        raise NotFound()
