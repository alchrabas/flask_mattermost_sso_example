from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()


class Client(db.Model):
    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True, nullable=False)
    _redirect_uris = db.Column(db.Text)
    default_redirect_uri = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    def __init__(self, client_id, client_secret, redirect_uris, default_redirect_uri, default_scopes):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uris = redirect_uris
        self.default_redirect_uri = default_redirect_uri
        self.default_scopes = default_scopes

    @property
    def client_type(self):
        return 'public'

    @hybrid_property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @redirect_uris.setter
    def redirect_uris(self, value):
        self._redirect_uris = " ".join(value)

    @hybrid_property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    @default_scopes.setter
    def default_scopes(self, value):
        self._default_scopes = " ".join(value)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)

    def __init__(self, username, email):
        self.username = username
        self.email = email


class GrantToken(db.Model):
    __tablename__ = "grant_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
    user = db.relationship(User)
    client_id = db.Column(db.String(40), nullable=False)
    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class BearerToken(db.Model):
    __tablename__ = "bearer_tokens"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(40), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
