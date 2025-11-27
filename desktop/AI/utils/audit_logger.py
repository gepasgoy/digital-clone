import datetime
import json


class AuditLogger:
    def __init__(self, log_file="audit.log"):
        self.log_file = log_file

    def log(self, action, details):
        """Запись действия в журнал аудита"""
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'action': action,
            'details': details
        }

        # В реальном приложении здесь была бы запись в файл/БД
        print(f"AUDIT: {json.dumps(log_entry, ensure_ascii=False)}")

    def get_recent_logs(self, limit=50):
        """Получение последних записей (заглушка)"""
        return [f"Лог запись {i}" for i in range(limit)]