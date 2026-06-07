
from kivymd.app import MDApp

from kivymd.uix.screen import MDScreen

from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.label import MDLabel

from kivymd.uix.button import MDRaisedButton

from kivy.uix.image import Image

from kivy.clock import Clock

from kivy.graphics.texture import Texture

from kivy.core.window import Window

from kivy.metrics import dp

import cv2

from pyzbar.pyzbar import decode

from datetime import datetime

import sqlite3

import json

import os

import csv

from pathlib import Path


# ================= WINDOW =================

Window.size = (1100, 760)

Window.clearcolor = (0.93, 0.95, 0.97, 1)


# ================= LOAD SESSION =================

if os.path.exists("session.json"):

    with open("session.json", "r") as file:

        session_data = json.load(file)

else:

    session_data = {

        "duty_staff": "",

        "designation": "",

        "date": "",

        "venue": "",

        "session": ""
    }


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


# ================= APP =================

class ScannerApp(MDApp):

    def build(self):

        self.theme_cls.primary_palette = "Blue"

        self.theme_cls.theme_style = "Light"

        self.scanned_students = set()

        self.camera_running = False


        screen = MDScreen()


        # ================= MAIN LAYOUT =================

        main_layout = MDBoxLayout(

            orientation="vertical"
        )


        # ================= HEADER =================

        header = MDBoxLayout(

            orientation="vertical",

            size_hint_y=None,

            height=dp(90)
        )


        top_bar = MDBoxLayout(

            size_hint_y=None,

            height=dp(50),

            md_bg_color=(0.02, 0.16, 0.38, 1)
        )


        title = MDLabel(

            text="PANIMALAR ENGINEERING COLLEGE",

            halign="center",

            bold=True,

            theme_text_color="Custom",

            text_color=(1, 1, 1, 1),

            font_style="H5"
        )


        top_bar.add_widget(title)


        second_bar = MDBoxLayout(

            size_hint_y=None,

            height=dp(40),

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


        # ================= CENTER =================

        center_layout = MDBoxLayout(

            orientation="vertical",

            padding=[0, dp(35), 0, 0]
        )


        # ================= CARD =================

        card = MDBoxLayout(

            orientation="vertical",

            spacing=dp(18),

            padding=[dp(35), dp(35), dp(35), dp(35)],

            size_hint=(None, None),

            size=(dp(780), dp(610)),

            pos_hint={"center_x": 0.5},

            md_bg_color=(1, 1, 1, 1),

            radius=[20, 20, 20, 20]
        )


        # ================= TITLE =================

        title_label = MDLabel(

            text="Scan Student QR Code",

            halign="center",

            bold=True,

            theme_text_color="Custom",

            text_color=(0.02, 0.16, 0.38, 1),

            font_style="H4",

            size_hint_y=None,

            height=dp(50)
        )


        # ================= CAMERA =================

        self.image = Image(

            size_hint=(None, None),

            size=(640, 360),

            pos_hint={"center_x": 0.5}
        )


        # ================= BUTTONS =================

        button_layout = MDBoxLayout(

            spacing=dp(15),

            adaptive_size=True,

            pos_hint={"center_x": 0.5}
        )


        self.start_button = MDRaisedButton(

            text="Start Scanning",

            md_bg_color=(0.10, 0.35, 0.75, 1),

            size_hint=(None, None),

            size=(dp(170), dp(50))
        )


        self.stop_button = MDRaisedButton(

            text="Stop Scanning",

            md_bg_color=(0.85, 0.15, 0.15, 1),

            size_hint=(None, None),

            size=(dp(170), dp(50))
        )


        self.finish_button = MDRaisedButton(

            text="Finish Scanning",

            md_bg_color=(0.05, 0.50, 0.20, 1),

            size_hint=(None, None),

            size=(dp(170), dp(50))
        )


        self.start_button.bind(

            on_release=self.start_camera
        )


        self.stop_button.bind(

            on_release=self.stop_camera
        )


        self.finish_button.bind(

            on_release=self.finish_scanning
        )


        button_layout.add_widget(self.start_button)

        button_layout.add_widget(self.stop_button)

        button_layout.add_widget(self.finish_button)


        # ================= STUDENT TITLE =================

        student_title = MDLabel(

            text="Scanned Students",

            halign="center",

            bold=True,

            theme_text_color="Custom",

            text_color=(0.02, 0.16, 0.38, 1),

            font_style="H5",

            size_hint_y=None,

            height=dp(40)
        )


        # ================= STUDENT LIST =================

        self.student_list = MDLabel(

            text="No Students Scanned Yet",

            halign="center",

            theme_text_color="Primary"
        )


        # ================= ADD WIDGETS =================

        card.add_widget(title_label)

        card.add_widget(self.image)

        card.add_widget(button_layout)

        card.add_widget(student_title)

        card.add_widget(self.student_list)


        wrapper = MDBoxLayout(

            orientation="vertical",

            adaptive_height=True,

            pos_hint={"center_x": 0.5}
        )


        wrapper.add_widget(card)

        center_layout.add_widget(wrapper)


        main_layout.add_widget(header)

        main_layout.add_widget(center_layout)

        screen.add_widget(main_layout)


        # ================= AUTO START CAMERA =================

        Clock.schedule_once(

            lambda dt:

            self.start_camera(None),

            1
        )

        return screen


    # ================= START CAMERA =================

    def start_camera(self, instance):

        if not self.camera_running:

            self.capture = cv2.VideoCapture(

                0,

                cv2.CAP_DSHOW
            )

            self.capture.set(

                cv2.CAP_PROP_FRAME_WIDTH,

                1280
            )

            self.capture.set(

                cv2.CAP_PROP_FRAME_HEIGHT,

                720
            )

            self.camera_running = True

            Clock.schedule_interval(

                self.update_camera,

                1.0 / 30.0
            )


    # ================= STOP CAMERA =================

    def stop_camera(self, instance):

        if self.camera_running:

            Clock.unschedule(

                self.update_camera
            )

            self.capture.release()

            self.camera_running = False


    # ================= UPDATE CAMERA =================

    def update_camera(self, dt):

        success, frame = self.capture.read()

        if not success:

            return


        qr_codes = decode(frame)


        for qr in qr_codes:

            qr_data = qr.data.decode(

                'utf-8'
            ).strip()


            # ================= DUPLICATE CHECK =================

            if qr_data not in self.scanned_students:

                self.scanned_students.add(qr_data)


                scan_time = datetime.now().strftime(

                    "%d-%m-%Y %H:%M:%S"
                )


                # ================= SAVE DATABASE =================

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


                # ================= BEEP =================

                try:

                    import winsound

                    winsound.Beep(1500, 300)

                except:

                    pass


                # ================= UPDATE STUDENT LIST =================

                self.student_list.text = "\n".join(

                    self.scanned_students
                )


                print(

                    f"{qr_data} Scanned Successfully"
                )

            else:

                print(

                    f"{qr_data} Already Scanned"
                )


            # ================= QR BOX =================

            points = qr.polygon


            if len(points) == 4:

                pts = []

                for point in points:

                    pts.append(

                        (point.x, point.y)
                    )

                for i in range(4):

                    cv2.line(

                        frame,

                        pts[i],

                        pts[(i + 1) % 4],

                        (255, 255, 255),

                        4
                    )


        # ================= SHOW CAMERA =================

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


    # ================= EXPORT CSV =================

    def export_csv(self):

        try:

            downloads_path = str(

                Path.home() / "Downloads"
            )

            file_name = f'''

Attendance_{session_data["date"]}_{session_data["session"]}.csv

'''.replace(" ", "_").replace("\n", "")

            file_path = os.path.join(

                downloads_path,

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

                f"\nCSV Saved Successfully:\n{file_path}"
            )

        except Exception as e:

            print(

                "CSV Export Error:",

                e
            )


    # ================= FINISH =================

    def finish_scanning(self, instance):

        self.stop_camera(None)

        self.export_csv()

        self.stop()


    # ================= SAFE CLOSE =================

    def on_stop(self):

        if self.camera_running:

            self.capture.release()

        conn.close()


ScannerApp().run()

