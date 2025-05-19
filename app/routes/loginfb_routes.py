from flask import Blueprint, render_template, request, redirect, url_for, session
from app.extension import oauth

loginfb_blueprint = Blueprint('loginfb', __name__)

@loginfb_blueprint.route('/login/facebook')
def login_facebook():
    next_page = request.args.get('next')
    if next_page:
        session['next_page'] = next_page
        
    redirect_uri = url_for('loginfb.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@loginfb_blueprint.route('/login/facebook/callback')
def facebook_callback():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get('me?fields=id,name,email,picture')
    user_info = resp.json()

    session['user_id'] = user_info['id']
    session['user_name'] = user_info['name']
    session['user_avatar'] = user_info['picture']['data']['url']

    next_page = session.pop('next_page', None)
    if next_page and '/page2' in next_page:
        return redirect('/page2')
    elif next_page and '/page3' in next_page:
        return redirect('/page3')
    elif next_page and '/page4' in next_page:
        return redirect('/page4')
    elif next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('main.index'))