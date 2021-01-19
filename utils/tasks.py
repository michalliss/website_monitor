import multiprocessing
import urllib.request
from datetime import datetime, timedelta

from apscheduler.events import EVENT_JOB_EXECUTED
from pythonping import ping
from sqlalchemy import desc
from project import scheduler, db
from project.models import Website, WebsiteStatus

headers={'User-Agent': 'Mozilla/5.0'}


@scheduler.task('interval', id='WebsiteHealth', seconds=30, misfire_grace_time=900)
def update_websites():
    """
    Updates website statuses. It is scheduled to run in intervals.
    """
    with scheduler.app.app_context():
        websites = Website.query.all()
        urls = [ws.url for ws in websites]
        num_threads = 16
        p = multiprocessing.Pool(num_threads)
        result = p.map(ping_website, urls)

        for i, website in enumerate(websites):
            alive = result[i] is not None
            latency = result[i]
            previous_status = WebsiteStatus.query.filter_by(website_id=website.id).order_by(
                desc(WebsiteStatus.timestamp)).first()
            new_status = WebsiteStatus(alive=alive, latency=latency, website_id=website.id)
            if previous_status != None and previous_status.alive != alive:
                if alive:
                    pass
                else:
                    website.notify()
            website.status.append(new_status)
            db.session.add(new_status)
        db.session.commit()


def ping_website(url):
    """
    Pings website. Returns latency or None if website did not respond.
    :param url: Url of website to ping
    :return: Latency
    """
    try:
        req = urllib.request.Request("http://" + url, headers=headers)
        alive = urllib.request.urlopen(req, timeout=3).getcode() == 200
        result = ping(url, verbose=False, timeout=1)
        if alive and result.success():
            return result.rtt_avg_ms
        else:
            return None
    except Exception as e:
        return None


@scheduler.task('interval', id='TrimOld', days=1, misfire_grace_time=900)
def trim_old_status():
    """
    Removes website statuses that are older than a week. It is scheduled to run every day.
    """
    with scheduler.app.app_context():
        current_time = datetime.utcnow()
        week_ago = current_time - timedelta(weeks=1)
        db.session.query(WebsiteStatus).filter(WebsiteStatus.timestamp < week_ago).delete()
        db.session.commit()


def finish_listener(event):
    with scheduler.app.app_context():
        if not event.job_id.startswith("ws"):
            return
        print(event.job_id)
        website_id = event.job_id[2::]
        finished_website = Website.query.get(website_id)
        if finished_website is not None:
            finished_website.attack = False
        db.session.add(finished_website)
        db.session.commit()
        print("Finished attack" + "ws")


scheduler.add_listener(finish_listener, EVENT_JOB_EXECUTED)
