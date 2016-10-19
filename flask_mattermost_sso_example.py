import datetime
import json

from flask import Flask
from flask import request
from flask_login import login_required, current_user
from flask_oauthlib.provider import OAuth2Provider

from models import db, GrantToken, BearerToken, Client, User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root@localhost/example_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

oauth = OAuth2Provider(app)
db.init_app(app)


@app.route("/api/v3/user")
@oauth.require_oauth("login")
def sso_user_info_for_mattermost():
    user = request.oauth.user
    return json.dumps({"id": user.id,
                       "username": user.username,
                       "login": user.username,
                       "email": user.email,
                       "name": user.username,
                       })


@oauth.clientgetter
def load_client(requested_client_id):
    return Client.query.filter_by(id=requested_client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return GrantToken.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request):
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
    grant = GrantToken(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()

    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return BearerToken.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return BearerToken.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, _request):
    existing_tokens = BearerToken.query.filter_by(
        client_id=_request.client.client_id,
        user_id=_request.user.id
    )
    # make sure that every client has only one token connected to a user
    for existing_bearer_token in existing_tokens:
        db.session.delete(existing_bearer_token)
    expires_in = token.pop('expires_in')
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    new_token = BearerToken(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=_request.client.client_id,
        user_id=_request.user.id,
    )
    db.session.add(new_token)
    db.session.commit()
    return new_token


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
@login_required
def authorize(*args, **kwargs):
    return True


@app.route('/oauth/token', methods=["GET", "POST"])
@oauth.token_handler
def access_token():
    return None


@app.before_first_request
def create_database():
    db.create_all()
    if not Client.query.count():
        db.session.add(Client(
            client_id="<your-client-id>",
            client_secret="<your-client-secret>",
            redirect_uris=["<your-mattermost-url>/signup/gitlab/complete",
                           "<your-mattermost-url>/login/gitlab/complete"],
            default_redirect_uri="<your-mattermost-url>/signup/gitlab/complete",
            default_scopes=["login"]
        ))
        db.session.add(User("test_user", "test@exeris.org"))
    db.session.commit()


if __name__ == '__main__':
    app.run()
