from django.apps import AppConfig


class MarketConfig(AppConfig):
    name = "market"

    def ready(self):
        from .jobs import start_market_jobs_scheduler

        start_market_jobs_scheduler()
