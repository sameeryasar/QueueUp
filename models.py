"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

def get_user():
    return auth.current_user.get('id') if auth.current_user else None


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'profiles',
    Field('user', 'reference auth_user'),
    Field('region', default="NA West"),
    Field('bio'),
    Field('mic', 'boolean', default=False),
    Field('tiltproof', 'integer', default=0),
    Field('leader', 'integer', default=0 ),
    Field('fun', 'integer', default=0),
    Field('communicative', 'integer', default=0)
)

db.define_table(
    'game_data',
    Field('profile', 'reference profiles'),
    Field('game'),
    Field('gamertag', default="No Name"),
    Field('rank', default="Unranked"),
)

db.define_table(
    'lobbies',
    Field('leader'),
    Field('bio'),
    Field('player1'),
    Field('player2'),
    Field('player3'),
    Field('player4'),
    Field('rank'),
    Field('region'),
    Field('playstyle'),
    Field('microphone'),
)

db.commit()
