from apscheduler.schedulers.background import BackgroundScheduler
from discApp.service import couponScheduler



def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(couponScheduler, 'interval', minutes=5, id='apcheduler_1', replace_existing=True)
    scheduler.start()