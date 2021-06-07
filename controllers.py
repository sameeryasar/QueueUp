"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses(auth.user, url_signer, db, 'index.html')
def index():
    print("looking good so far")
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
    )

@action('profile')
@action.uses(auth.user, url_signer, db, 'profile.html')
def profile():
    print("profile page reached")
    user_info = db(db.auth_user.email == get_user_email()).select().first()
    
    if not db(db.profiles.user == user_info.id).select().first():
        db.profiles.insert(
            user=user_info.id,
            region=db.profiles.region.default,
            bio=db.profiles.bio.default,
            mic=db.profiles.mic.default,
            tiltproof=db.profiles.tiltproof.default,
            leader=db.profiles.leader.default,
            fun=db.profiles.fun.default,
            communicative=db.profiles.communicative.default,
            )      
    
    profile_info = db(db.profiles.user == user_info.id).select().first()

    return dict(
        user_info=user_info,
        profile_info=profile_info,
        change_profile_url = URL('change_profile', signer=url_signer),
        add_game_url = URL('add_game', signer=url_signer),
    )

@action('change_profile', method="POST")
@action.uses(auth.user, url_signer.verify(), db)
def change_profile():
    print("changing the profile apparently")
    user_info = db(db.auth_user.email == get_user_email()).select().first()
    profile_info = db(db.profiles.user == user_info.id).select().first()
    auth_user_id = db.auth_user.update_or_insert(
        db.auth_user.email == get_user_email(),
        email = request.json.get('email') if request.json.get('email') != "" else user_info.email,
        first_name = request.json.get('first_name') if request.json.get('first_name') != "" else user_info.first_name,
        last_name = request.json.get('last_name') if request.json.get('last_name') != "" else user_info.last_name,
    )
    profile_id = db.profiles.update_or_insert(
        db.profiles.user == user_info.id,
        region = request.json.get('region') if request.json.get('region') != "" else profile_info.region,
        bio = request.json.get('bio') if request.json.get('bio') != "" else profile_info.bio,
        mic = request.json.get('mic') if request.json.get('mic') is not None else profile_info.mic,
    )
    return dict(
        auth_user_id=auth_user_id,
        profile_id=profile_id,
    )

@action('add_game', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_game():
    print("adding some game data")
    user_info = db(db.auth_user.email == get_user_email()).select().first()
    profile_info = db(db.profiles.user == user_info.id).select().first()
    game_to_add = request.json.get('game')
    print(game_to_add)

    game_data = db.game_data.update_or_insert(
        (db.game_data.profile == profile_info.id) & (db.game_data.game == game_to_add),
        profile = profile_info.id,
        game = game_to_add,
        gamertag = request.json.get('gamertag'),
        rank = request.json.get('rank'),
    )

    return dict(
        game_data=game_data,
    )

@action('lobbies')
@action.uses(auth.user, url_signer, db, 'lobbies.html')
def lobbies():
    print("lobby page reached")
    return dict(
        # URLS used for callbacks and HTTP requests
        add_lobby_url = URL('add_lobby', signer=url_signer),
        load_lobbies_url = URL('load_lobbies', signer=url_signer)
    )

@action('add_lobby', method="POST")
@action.uses(auth.user, url_signer.verify(), db)
def add_contact():
    print("adding a lobby ig")
    r = db(db.auth_user.email == get_user_email()).select().first()
    lobby_leader = r.first_name + " " + r.last_name if r is not None else "Unknown"
    members = ["player1", "player2", "player3", "player4"]
    id = db.lobbies.insert(
        leader = lobby_leader, # get this with get_user probably
        bio = request.json.get('bio'),
        rank = request.json.get('rank'),
        region = request.json.get('region'),
        playstyle = request.json.get('playstyle'),
        player1 = "player1",
        player2 = "player2",
        player3 = "player3",
        player4 = "player4",
        microphone = "yes",
    )
    return dict(
        id=id,
        leader=lobby_leader,
        members=members,
    )

@action('load_lobbies')
@action.uses(url_signer.verify(), db)
def load_lobbies():
    lobbies = db(db.lobbies).select().as_list()
    return dict(lobbies=lobbies)
