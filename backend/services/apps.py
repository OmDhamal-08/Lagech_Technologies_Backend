from django.apps import AppConfig


class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'

    def ready(self):
        """Start the hourly report scheduler when Django boots."""
        import os
        # Only start in the main process (not in management commands or migrations)
        if os.environ.get('RUN_MAIN') == 'true':
            try:
                from .scheduler import start_scheduler
                start_scheduler()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Scheduler start failed: {e}")
