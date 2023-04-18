from django.apps import AppConfig



class DiscappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discounts'

    def ready(self):
        print(
            'Starting Scheduler'
        )
        from .scheuler import coupon_scheduler
        coupon_scheduler.start()
