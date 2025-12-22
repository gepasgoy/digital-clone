class InactivityTimer:
    def __init__(self, root, logout_callback, timeout=10000):
        self.root = root
        self.logout_callback = logout_callback
        self.timeout = timeout
        self.timer_id = None
        self.is_running = False

        # Привязка событий активности
        self.bind_events()

    def bind_events(self):
        """Привязка событий для отслеживания активности"""
        events = ['<KeyPress>', '<ButtonPress>', '<Motion>']
        for event in events:
            self.root.bind(event, self.reset_timer, add='+')

    def start(self):
        """Запуск таймера неактивности"""
        self.is_running = True
        self.reset_timer()

    def stop(self):
        """Остановка таймера"""
        self.is_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def reset_timer(self, event=None):
        """Сброс таймера при активности"""
        if not self.is_running:
            return

        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        self.timer_id = self.root.after(self.timeout, self.logout_callback)

    def get_remaining_time(self):
        """Получение оставшегося времени (приблизительно)"""
        return self.timeout