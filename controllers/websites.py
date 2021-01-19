import urllib
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy import desc, and_, func
from validator_collection import checkers

from project import db
from project import scheduler
from project.utils.attack import SlowLorisAttack
from project.models import Website, Following, WebsiteStatus

websites = Blueprint('websites', __name__)


@websites.route('/add_website', methods=['POST'])
@login_required
def add_website():
    """
    Follows website. If the website is not already tracked it is added.
    """
    url = request.form.get('website')
    if not (url.startswith('//') or url.startswith('http://') or url.startswith('https://')):
        url = 'http://' + url
    url = urllib.parse.urlparse(url)
    url = url.netloc
    if (not checkers.is_url("http://" + url) and not checkers.is_ipv4(url)) or url == "":
        flash('URL is incorrect')
        return redirect(url_for('main.websites'))

    existing_ws = Website.query.filter_by(url=url).first()
    if existing_ws is None:
        existing_ws = Website()
        existing_ws.url = url
        db.session.add(existing_ws)

    following = Following.query.get((current_user.id, existing_ws.id))
    if following is not None:
        flash("You're already following this website!")
        return redirect(url_for('main.websites'))

    a = Following()
    a.website = existing_ws
    a.send_mail = False
    a.user = current_user

    user = current_user
    user.websites.append(a)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('main.websites'))


@websites.route('/unfollow_website', methods=['POST'])
@login_required
def unfollow_website():
    """
    Deletes following entry from database. If there are no users following mentioned website, the website entry is also removed
    """
    website_id = request.form.get('website')

    following = Following.query.get((current_user.id, website_id))
    delete_website = True if len(following.website.users) == 1 else False

    if delete_website:
        WebsiteStatus.query.filter_by(website_id=website_id).delete()
        ws = Website.query.get(website_id)
        db.session.delete(ws)
    else:
        db.session.delete(following)

    db.session.commit()
    return redirect(url_for('main.websites'))


@websites.route('/mail_website', methods=['POST'])
@login_required
def mail_website():
    """
    Flips the user preference regarding sending mails on page inavaliability
    """
    website_id = request.form.get('website')
    following = Following.query.get((current_user.id, website_id))
    following.send_mail = not following.send_mail
    db.session.add(following)
    db.session.commit()
    return redirect("/website/" + website_id)


@websites.route('/get_website/<ws_id>/<num>', methods=['GET'])
def get_website(ws_id, num):
    """
    Fetches website status
    :param ws_id: Id of website
    :param num: Number of last status to fetch
    """
    num = int(num)
    if num == 0:
        status = WebsiteStatus.query.filter_by(website_id=ws_id).order_by(desc(WebsiteStatus.timestamp)).all()
    else:
        status = WebsiteStatus.query.filter_by(website_id=ws_id).order_by(desc(WebsiteStatus.timestamp)).limit(
            num).all()

    if status:
        latencies = [s.latency for s in status[::-1]]
        times = [s.timestamp.strftime("%m/%d %H:%M:%S") for s in status[::-1]]
        return jsonify(latencies=latencies, times=times)
    else:
        return jsonify(latencies=[], times=[])


@websites.route('/status_days/<ws_id>/<num>', methods=['GET'])
def status_days(ws_id, num):
    """
    Fetches percentage of availability of website in last <num> days
    :param ws_id: Id of website
    :param num: Number of days to fetch
    """
    num = int(num)
    if not 0 < num < 7:
        return jsonify(latencies=[], times=[])
    days = []
    times = []

    for i in reversed(range(num)):
        current_time = datetime.utcnow()
        ago1 = current_time - timedelta(days=i)
        status = db.session.query(WebsiteStatus).filter(
            and_(WebsiteStatus.website_id == ws_id, ago1.date() == func.DATE(WebsiteStatus.timestamp))).all()

        if len(status) != 0:
            percentage = int(10000 * len(list(filter(lambda x: x.alive is True, status))) / len(status)) / 100
        else:
            percentage = None
        days.append(percentage)
        times.append(str(ago1.date()))

    return jsonify(percentage=days, times=times)


@websites.route('/run_attack', methods=['POST'])
@login_required
def attack_website():
    """
    Runs attack on a website
    """
    website_id = request.form.get('website')
    timeout = int(request.form.get('timeout'))
    attack_type = request.form.get('attack')

    if attack_type == "Slow Loris":
        attack = SlowLorisAttack()
    else:
        return jsonify(success=False)

    if not 0 < timeout <= 60:
        return jsonify(success=False)

    website = Website.query.get(website_id)
    if website.attack:
        return jsonify(success=False)

    website.attack = True
    db.session.add(website)
    db.session.commit()

    scheduler.add_job(id="ws" + website_id, func=attack.run, args=[website.url, timeout])
    print("Started attack" + "ws" + website_id)

    return jsonify(success=True)


@websites.route('/attack_status/<ws_id>', methods=['GET'])
def attack_status(ws_id):
    """
    Fetches status of attack
    :param ws_id: Website id
    """
    website = Website.query.get(ws_id)
    return jsonify(running=website.attack)
