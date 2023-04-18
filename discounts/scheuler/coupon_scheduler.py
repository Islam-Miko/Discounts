from apscheduler.schedulers.background import BackgroundScheduler
from discounts.service import couponScheduler



def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(couponScheduler, 'interval', minutes=1, id='apcheduler_1', replace_existing=True)
    scheduler.start()