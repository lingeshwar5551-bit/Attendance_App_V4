
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image

import cv2
from datetime import datetime

import sqlite3
import csv
import os


# ================= WINDOW =================

Window.size = (1480, 820)
Window.clearcolor = (0.93, 0.95, 0.97, 1)


# ================= DATABASE =================

if not os.path.exists("database"):
    os.makedirs("database")

conn = sqlite3.connect(
    "database/attendance.db"
)

cursor = conn.cursor()

cursor.execute(

    '''

    CREATE TABLE IF NOT EXISTS attendance(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        roll_no TEXT,

        duty_staff TEXT,

        designation TEXT,

        date TEXT,

        venue TEXT,

        session TEXT,

        scan_time TEXT
    )

    '''
)

conn.commit()


# ================= SESSION DATA =================

session_data = {

    "duty_staff": "",

    "designation": "",

    "date": "",

    "venue": "",

    "session": ""
}


# ================= FORM SCREEN =================

class FormScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        main_layout = MDBoxLayout(
            orientation="vertical"
        )

        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120)
        )

        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(75),
            md_bg_color=(0.02, 0.16, 0.38, 1)
        )

        title = MDLabel(
            text="PANIMALAR ENGINEERING COLLEGE",
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H4"
        )

        top_bar.add_widget(title)

        second_bar = MDBoxLayout(
            size_hint_y=None,
            height=dp(45),
            md_bg_color=(0.07, 0.24, 0.48, 1)
        )

        subtitle = MDLabel(
            text="Career Guidance Monitoring System",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        second_bar.add_widget(subtitle)

        header.add_widget(top_bar)
        header.add_widget(second_bar)

        center_layout = MDBoxLayout(
            orientation="vertical",
            padding=[0, dp(40), 0, 0]
        )

        card = MDBoxLayout(
            orientation="vertical",
            spacing=dp(22),
            padding=[dp(35), dp(35), dp(35), dp(35)],
            size_hint=(None, None),
            size=(dp(570), dp(610)),
            pos_hint={"center_x": 0.5},
            md_bg_color=(1, 1, 1, 1),
            radius=[20, 20, 20, 20]
        )

        form_title = MDLabel(
            text="Career Guidance Session Portal",
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.02, 0.16, 0.38, 1),
            font_style="H4",
            size_hint_y=None,
            height=dp(60)
        )

        self.duty_staff = MDTextField(
            hint_text="Duty Staff Name",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55)
        )

        self.designation_button = MDRaisedButton(
            text="Select Designation",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(1, 1, 1, 1),
            text_color=(0, 0, 0, 1)
        )

        designation_items = [

            {
                "text": "Professor",
                "on_release": lambda x="Professor":
                self.set_designation(x)
            },

            {
                "text": "Associate Professor",
                "on_release": lambda x="Associate Professor":
                self.set_designation(x)
            },

            {
                "text": "Assistant Professor",
                "on_release": lambda x="Assistant Professor":
                self.set_designation(x)
            },

            {
                "text": "Assistant Professor LO",
                "on_release": lambda x="Assistant Professor LO":
                self.set_designation(x)
            }
        ]

        self.designation_menu = MDDropdownMenu(
            caller=self.designation_button,
            items=designation_items,
            width_mult=4
        )

        self.designation_button.bind(
            on_release=lambda x:
            self.designation_menu.open()
        )

        self.date = MDTextField(
            hint_text="Date",
            text=str(datetime.now().date()),
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55)
        )

        self.venue = MDTextField(
            hint_text="Venue",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(55)
        )

        self.session_button = MDRaisedButton(
            text="Select Session",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(1, 1, 1, 1),
            text_color=(0, 0, 0, 1)
        )

        session_items = [

            {
                "text": "FN",
                "on_release": lambda x="FN":
                self.set_session(x)
            },

            {
                "text": "AN",
                "on_release": lambda x="AN":
                self.set_session(x)
            }
        ]

        self.session_menu = MDDropdownMenu(
            caller=self.session_button,
            items=session_items,
            width_mult=3
        )

        self.session_button.bind(
            on_release=lambda x:
            self.session_menu.open()
        )

        start_button = MDRaisedButton(
            text="Start Scanning",
            size_hint=(1, None),
            height=dp(58),
            md_bg_color=(0.10, 0.35, 0.75, 1),
            font_size="20sp"
        )

        start_button.bind(
            on_release=self.start_scanning
        )

        card.add_widget(form_title)
        card.add_widget(self.duty_staff)
        card.add_widget(self.designation_button)
        card.add_widget(self.date)
        card.add_widget(self.venue)
        card.add_widget(self.session_button)

        card.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(10)
            )
        )

        card.add_widget(start_button)

        wrapper = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            pos_hint={"center_x": 0.5}
        )

        wrapper.add_widget(card)

        center_layout.add_widget(wrapper)

        footer = MDLabel(
            text="Career Guidance and Placement Monitoring Portal",
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(40)
        )

        main_layout.add_widget(header)
        main_layout.add_widget(center_layout)
        main_layout.add_widget(footer)

        self.add_widget(main_layout)

    def set_designation(self, value):

        self.designation_button.text = value
        self.designation_menu.dismiss()

    def set_session(self, value):

        self.session_button.text = value
        self.session_menu.dismiss()

    def start_scanning(self, instance):

        if (
            self.duty_staff.text.strip() == "" or
            self.designation_button.text == "Select Designation" or
            self.date.text.strip() == "" or
            self.venue.text.strip() == "" or
            self.session_button.text == "Select Session"
        ):

            print("Please Fill All Fields")
            return

        session_data["duty_staff"] = self.duty_staff.text
        session_data["designation"] = self.designation_button.text
        session_data["date"] = self.date.text
        session_data["venue"] = self.venue.text
        session_data["session"] = self.session_button.text

        cursor.execute(

            '''

            DELETE FROM attendance

            WHERE

                date = ?

            AND

                session = ?

            ''',

            (

                session_data["date"],
                session_data["session"]
            )
        )

        conn.commit()

        self.manager.current = "scanner"


# ================= SCANNER SCREEN =================

class ScannerScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.scanned_students = set()
        self.camera_running = False

        self.detector = cv2.QRCodeDetector()

        layout = MDBoxLayout(
            orientation="vertical"
        )

        self.image = Image(
            size_hint=(1, 1)
        )

        button_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15),
            padding=dp(10)
        )

        start_btn = MDRaisedButton(
            text="Start Scanning",
            md_bg_color=(0.10, 0.35, 0.75, 1)
        )

        stop_btn = MDRaisedButton(
            text="Stop Scanning",
            md_bg_color=(0.85, 0.15, 0.15, 1)
        )

        finish_btn = MDRaisedButton(
            text="Finish Scanning",
            md_bg_color=(0.05, 0.50, 0.20, 1)
        )

        start_btn.bind(on_release=self.start_camera)
        stop_btn.bind(on_release=self.stop_camera)
        finish_btn.bind(on_release=self.finish_scanning)

        button_layout.add_widget(start_btn)
        button_layout.add_widget(stop_btn)
        button_layout.add_widget(finish_btn)

        self.student_list = MDLabel(
            text="No Students Scanned Yet",
            halign="center"
        )

        layout.add_widget(self.image)
        layout.add_widget(button_layout)
        layout.add_widget(self.student_list)

        self.add_widget(layout)

    def start_camera(self, instance):

        if not self.camera_running:

            self.scanned_students.clear()

            self.student_list.text = "No Students Scanned Yet"

            self.capture = cv2.VideoCapture(0)

            self.camera_running = True

            Clock.schedule_interval(
                self.update_camera,
                1.0 / 30.0
            )

    def stop_camera(self, instance):

        if self.camera_running:

            Clock.unschedule(
                self.update_camera
            )

            self.capture.release()

            self.camera_running = False

    def update_camera(self, dt):

        success, frame = self.capture.read()

        if not success:
            return

        data, bbox, _ = self.detector.detectAndDecode(frame)

        if data:

            qr_data = data.strip()

            if qr_data not in self.scanned_students:

                self.scanned_students.add(qr_data)

                scan_time = datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                cursor.execute(

                    '''

                    INSERT INTO attendance(

                        roll_no,

                        duty_staff,

                        designation,

                        date,

                        venue,

                        session,

                        scan_time

                    )

                    VALUES(?, ?, ?, ?, ?, ?, ?)

                    ''',

                    (

                        qr_data,

                        session_data["duty_staff"],

                        session_data["designation"],

                        session_data["date"],

                        session_data["venue"],

                        session_data["session"],

                        scan_time
                    )
                )

                conn.commit()

                self.student_list.text = "\n".join(
                    self.scanned_students
                )

                print(
                    f"{qr_data} Scanned Successfully"
                )

        buf = cv2.flip(frame, 0).tobytes()

        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]),
            colorfmt='bgr'
        )

        texture.blit_buffer(
            buf,
            colorfmt='bgr',
            bufferfmt='ubyte'
        )

        self.image.texture = texture

    def export_csv(self):

        try:

            downloads_path = os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            )

            output_folder = os.path.join(
                downloads_path,
                "Attendance_Reports"
            )

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            file_name = f"Attendance_{session_data['date']}_{session_data['session']}.csv"

            file_name = file_name.replace(" ", "_")

            file_path = os.path.join(
                output_folder,
                file_name
            )

            cursor.execute(

                '''

                SELECT roll_no

                FROM attendance

                WHERE

                    date = ?

                AND

                    session = ?

                ''',

                (

                    session_data["date"],
                    session_data["session"]
                )
            )

            students = cursor.fetchall()

            if len(students) == 0:

                print("No Students Found")
                return

            with open(
                file_path,
                mode="w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Date",
                    "Duty Faculty",
                    "Designation",
                    "Session",
                    "Venue",
                    "Present"
                ])

                first = True

                for student in students:

                    if first:

                        writer.writerow([

                            session_data["date"],

                            session_data["duty_staff"],

                            session_data["designation"],

                            session_data["session"],

                            session_data["venue"],

                            student[0]
                        ])

                        first = False

                    else:

                        writer.writerow([
                            "",
                            "",
                            "",
                            "",
                            "",
                            student[0]
                        ])

            print(
                f"\nCSV SAVED SUCCESSFULLY\n{file_path}"
            )

        except Exception as e:

            print(
                "CSV EXPORT ERROR:",
                e
            )

    def finish_scanning(self, instance):

        self.stop_camera(None)

        self.export_csv()

        self.manager.current = "form"


# ================= APP =================

class AttendanceApp(MDApp):

    def build(self):

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        sm = ScreenManager()

        sm.add_widget(
            FormScreen(name="form")
        )

        sm.add_widget(
            ScannerScreen(name="scanner")
        )

        return sm

    def on_stop(self):

        conn.close()


AttendanceApp().run()

