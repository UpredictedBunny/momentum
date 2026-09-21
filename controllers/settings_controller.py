from database.db_manager import get_db
from config.settings import settings

class SettingsController:
    def backup(self): return get_db().backup_now()
    def info(self): return {"name":settings.app.name,"version":settings.app.version,"database":str(settings.resolve_path(settings.database.path))}
