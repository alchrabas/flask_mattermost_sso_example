# Flask SSO Provider for Mattermost

Mattermost Team Edition allows two login methods:

 - standard login and password
 - single-sign on using GitLab account

GitLab SSO uses OAuth2 standard and Mattermost allows setting links to any site to define endpoints
used by Mattermost SSO client, so with some effort it's possible to pretend your flask application
is a self-hosted GitLab instance.

The code was originally used to introduce single-sign-on for chat for
[Exeris](https://github.com/alchrabas/exeris) - my open-source crafting and exploration game -
but I've simplified the code excerpt so it can be reused in other projects.

I've used Flask-OAuthlib, because I've needed Flask anyway, but it's probably very similar with bare oauthlib.
The user accounts are managed by Flask-login to simplify the process.

`/oauth/authorize` endpoint is requested by the client's browser during the login process, but
`/oauth/token` and `/api/v3/user` are exchanged between the Mattermost server and Flask SSO provider,
so it's not possible to use Flask-Login's `current_user` in these functions.

There's a problem with Oauthlib library as it doesn't accept authorization requests with an empty scope.
It's a bug that wasn't fixed at the moment of commiting my code.

Unfortunately it's not possible to specify any scope in Mattermost admin panel, but it's possible in the config file
(you need access to Mattermost server's filesystem, though).

I have mattermost installed in /opt/mattermost/ directory, so in my case to change the config I did:

```
vim /opt/mattermost/config/config.json
```

The interesting part is "GitLabSettings" and you should make it look like that:
```
"GitLabSettings": {
    "Enable": true,
    "Secret": "<your-client-secret>",
    "Id": "<your-client-id>",
    "Scope": "login",
    "AuthEndpoint": "<your-flask-app-url>/oauth/authorize",
    "TokenEndpoint": "<your-flask-app-url>/oauth/token",
    "UserApiEndpoint": "<your-flask-app-url>/api/v3/user"
},
```

Client secret and client id should be random strings, but there are no special requirements for a format.

Save the config and restart the mattermost to make sure the changes will work.
To make the flask app work you need to change the example code, especially the `create_database`
that populates the database with the data about the client (only one is needed) and Flask user accounts,
which are used to login to Mattermost. You need to update the Client values before you run the app:

```
db.session.add(Client(
client_id="<your-client-id>",
client_secret="<your-client-secret>",
redirect_uris=["<your-mattermost-url>/signup/gitlab/complete",
               "<your-mattermost-url>/login/gitlab/complete"],
default_redirect_uri="<your-mattermost-url>/signup/gitlab/complete",
default_scopes=["login"]
))
```
It's pretty straightforward. Client id and secret must be the same as set in Mattermost config.

You also need to configure SQLAlchemy to access the database. The default is:

```
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root@localhost/example_db"
```

After creating the required database you can run the app and test it.
Go to <your-mattermost-url> and click on "Sign in with GitLab" button.
You'll be redirected to your flask app's login page.

After logging in, Mattermost will try to log in onto account whose username is the same like the one of SSO provider.
If it doesn't exist then it will be created automatically.

This example is mostly based on
[Flask-OAuthlib documentation](https://flask-oauthlib.readthedocs.io/en/latest/oauth2.html), so most of the effort
was learning how to get around the problem with lack of scope and what keys need to be available
in the response from `/api/v3/user`.

The dict that needs to be returned by this endpoint needs to contain the following values:

```
{
    "id" - it must be an integer value, it should never change
    "username" - username, the one used for @mentions
    "login" - I'm not sure where it's used
    "email" - email address
    "name" - a full name
}
```

## Mattermost SSO login button
The last problem is the text on a button used to login using your flask app SSO provider.
The "GitLab" text may misguide users who'd not know what to do.

I wasn't able to find any clean solution, so the only way was to modify the output javascript file which is used by mattermost.
The text is set in `webapp/dist/main.*.js` file under "login.gitlab" key.

I've created a bash script (`replace_mattermost_sso_button_text.sh`) which needs to be run from the mattermost
main directory to make the process easier.

Remember the script needs to be run manually every time you upgrade mattermost.