from flask import Blueprint, render_template
from flask_login import login_required, current_user

from project.models import Website, Following, WebsiteStatus

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', user=current_user if current_user.is_authenticated else None)


@main.route('/websites')
@login_required
def websites():
    return render_template('websites.html', user=current_user, websites=current_user.websites)


@main.route('/website/<ws_id>')
@login_required
def website(ws_id):
    website = Website.query.get(ws_id)
    print(website.observers)
    following = Following.query.get((current_user.id, website.id))
    alive = WebsiteStatus.query.filter_by(website_id=ws_id, alive=True).count()
    all = WebsiteStatus.query.filter_by(website_id=ws_id).count()
    if all == 0:
        percentage = 100
    else:
        percentage = int(alive / all * 100)
    return render_template('website.html', website=website, user=current_user, following=following, percentage=percentage, attacks=["Slow Loris", "Temp attack"])