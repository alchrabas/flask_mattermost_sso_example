from setuptools import setup, find_packages

setup(
    name='flask_mattermost_sso_example',
    version='0.1',

    description='Flask application as GitLab OAuth2 provider for Mattermost login',
    long_description='Mattermost team edition allows single-sign-on using a GitLab account. '
                     'This example shows how to use custom SSO provider '
                     'instead of GitLab for logging in to Mattermost chat. Tokens are stored in SQLAlchemy',

    url='https://github.com/alchrabas/flask_mattermost_sso_example',

    author='GreeK',
    author_email='alchrabas@exeris.org',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='flask mattermost oauth2 single-sign-on sso',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['sqlalchemy', 'flask', 'flask-sqlalchemy',
                      'flask-login', 'oauthlib==1.1.2', 'Flask-OAuthlib', 'psycopg2'],

    extras_require={
        'dev': ['check-manifest'],
    },
)
