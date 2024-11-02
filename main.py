import json
import hashlib
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from plyer import notification
from kivy.uix.scrollview import ScrollView
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define the cleared JSON structure
cleared_json = {
    "students": [],
    "representatives": [],
    "announcements": []
}

# Write the cleared structure to the JSON file
with open('student_data.json', 'w') as f:
    json.dump(cleared_json, f, indent=4)

print("JSON file cleared successfully.")

# Set window background color (ICCT color scheme example)
Window.clearcolor = (0.9, 0.9, 1, 1)  # Light blue background

# Load student and representative data from JSON with error handling
def load_data():
    try:
        with open('student_data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"students": [], "representatives": [], "announcements": []}

data = load_data()

def save_data():
    with open('student_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.bind(size=self._update_rounded_rect, pos=self._update_rounded_rect)

    def _update_rounded_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 1)  # Change to desired color
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def animate_button_press(self, instance):
        anim = Animation(size=(self.width * 1.05, self.height * 1.05), t='out_back', duration=0.1)
        anim.start(self)

    def animate_button_release(self, instance):
        anim = Animation(size=(self.width, self.height), t='out_back', duration=0.1)
        anim.start(self)

class LoginScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        gradient = Image(source='gradient_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(gradient)

        logo = Image(source='icct_logo.png', size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5, 'top': 0.9})
        self.add_widget(logo)

        title_label = Label(text="ICCT College Event Management System",
                            font_size=32, bold=True,
                            size_hint=(0.8, 0.1),
                            pos_hint={'center_x': 0.5, 'top': 0.85},
                            color=(0, 0, 0, 1))
        self.add_widget(title_label)

        form_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.8, 0.5), pos_hint={'center_x': 0.5, 'top': 0.65})

        self.user_type_input = TextInput(hint_text="Enter 'student' or 'representative'",
                                          multiline=False, size_hint=(1, None),
                                          height=40,
                                          background_color=(1, 1, 1, 0.9),
                                          padding_y=[10, 10],
                                          foreground_color=(0, 0, 0, 1),
                                          hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.user_type_input)

        self.student_number_input = TextInput(hint_text="Enter Student Number or Username",
                                              multiline=False, size_hint=(1, None),
                                              height=40,
                                              background_color=(1, 1, 1, 0.9),
                                              padding_y=[10, 10],
                                              foreground_color=(0, 0, 0, 1),
                                              hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.student_number_input)

        self.password_input = TextInput(hint_text="Enter Password",
                                        multiline=False, password=True, size_hint=(1, None),
                                        height=40,
                                        background_color=(1, 1, 1, 0.9),
                                        padding_y=[10, 10],
                                        foreground_color=(0, 0, 0, 1),                                        hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.password_input)

        self.login_button = RoundedButton(text="Login", size_hint=(1, None), height=50,
                                          on_press=self.validate_user)
        form_layout.add_widget(self.login_button)

        self.register_button = RoundedButton(text="Register as Representative", size_hint=(1, None), height=50,
                                             on_press=self.show_registration)
        form_layout.add_widget(self.register_button)

        self.register_student_button = RoundedButton(text="Register as Student", size_hint=(1, None), height=50,
                                                     on_press=self.show_student_registration)
        form_layout.add_widget(self.register_student_button)

        self.error_message = Label(text='', color=(1, 0, 0, 1), size_hint=(1, None), height=30, pos_hint={'center_x': 0.5, 'top': 0.2})
        self.add_widget(self.error_message)

        self.add_widget(form_layout)

    def validate_user(self, instance):
        self.error_message.text = ''
        user_type = self.user_type_input.text.lower()
        student_number = self.student_number_input.text
        password = hash_password(self.password_input.text)

        if not student_number or not self.password_input.text:
            self.error_message.text = "Please fill in all fields."
            return

        if user_type == "student":
            student_info = next((student for student in data['students']
                                 if student.get('student_number') == student_number and student.get('password') == password), None)

            if student_info:
                self.show_dashboard(student_info)
            else:
                self.error_message.text = 'Invalid Student Number or Password'
        
        elif user_type == "representative":
            rep_info = next((rep for rep in data['representatives']
                             if rep.get('username') == student_number and rep.get('password') == password), None)

            if rep_info:
                self.show_rep_dashboard(rep_info)
            else:
                self.error_message.text = 'Invalid Representative Username or Password'
        
        else:
            self.error_message.text = "Please enter 'student' or 'representative'"

    def show_dashboard(self, student_info):
        dashboard = DashboardScreen(student_info)
        self.clear_widgets()
        self.add_widget(dashboard)

    def show_rep_dashboard(self, rep_info):
        rep_dashboard = RepresentativeDashboardScreen(rep_info)
        self.clear_widgets()
        self.add_widget(rep_dashboard)

    def show_registration(self, instance):
        registration_screen = RegistrationScreen()
        self.clear_widgets()
        self.add_widget(registration_screen)

    def show_student_registration(self, instance):
        student_registration_screen = StudentRegistrationScreen()
        self.clear_widgets()
        self.add_widget(student_registration_screen)

class DashboardScreen(FloatLayout):
    def __init__(self, student_info, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)

         # Gradient background
        gradient = Image(source='gradient_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(gradient)

        # Welcome message for students
        welcome_label = Label(
            text=f"Welcome {student_info.get('name', 'Student')}, Section: {student_info.get('section', 'N/A')}",
            font_size=24,
            color=(0, 0, 0, 1),
            bold=True,
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        self.add_widget(welcome_label)

         # Announcement Section Title
        announcement_title = Label(
            text="Announcements:",
            font_size=22,
            color=(0, 0, 0, 1),
            bold=True,
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.8}
        )
        self.add_widget(announcement_title)

        # Announcement container with rounded corners
        self.announcement_box = ScrollView(
            size_hint=(0.9, 0.6),
            pos_hint={'center_x': 0.5, 'top': 0.7},
            bar_width=10,
            bar_color=(0.2, 0.6, 0.8, 1),
            bar_inactive_color=(0.2, 0.6, 0.8, 0.5),
            effect_cls='ScrollEffect',
            scroll_type=['bars', 'content']
        )

        self.announcement_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )

        self.announcement_box.add_widget(self.announcement_layout)

        self.add_widget(self.announcement_box)

         # Fetch and display announcements
        self.display_announcements()

        # Logout button
        self.logout_button = RoundedButton(text="Logout", size_hint=(0.5, None), height=50,
                                            on_press=self.logout,
                                            pos_hint={'center_x': 0.5, 'bottom': 0.05})  # Position it at the bottom
        self.add_widget(self.logout_button)

    def display_announcements(self):
        announcements = data.get('announcements', [])
        if announcements:
            for announcement in announcements:
                announcement_label = Label(
                    text=announcement.get('announcement', 'No message'),
                    size_hint_y=None,
                    height=40,
                    color=(0, 0, 0, 1)  # Black text color for visibility
                )
                self.announcement_layout.add_widget(announcement_label)
                self.announcement_layout.height += announcement_label.height
        else:
            no_announcement_label = Label(
                text="No announcements available.",
                size_hint_y=None,
                height=40,
                color=(1, 0, 0, 1)  # Red text color for "No announcements"
            )
            self.announcement_layout.add_widget(no_announcement_label)
            self.announcement_layout.height += no_announcement_label.height

    def logout(self, instance):
        # Go back to the login screen
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LoginScreen())

class RepresentativeDashboardScreen(FloatLayout):
    def __init__(self, rep_info, **kwargs):
        super(RepresentativeDashboardScreen, self).__init__(**kwargs)
        self.rep_info = rep_info

        # Gradient background
        gradient = Image(source='gradient_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(gradient)

        # Welcome message for representatives
        welcome_label = Label(
            text=f"Welcome {self.rep_info.get('name', 'Representative')}",  # Use self.rep_info here
            font_size=24,
            color=(0, 0, 0, 1),
            bold=True,
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        self.add_widget(welcome_label)

        # Layout for buttons
        button_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.8, 0.3),
                                  pos_hint={'center_x': 0.5, 'top': 0.5})

        # Post Announcement Button
        post_announcement_button = RoundedButton(text="Post Announcement", size_hint=(1, None), height=50,
                                                 on_press=self.post_announcement)
        button_layout.add_widget(post_announcement_button)

        # Logout Button
        logout_button = RoundedButton(text="Logout", size_hint=(1, None), height=50,
                                      on_press=self.confirm_logout)
        button_layout.add_widget(logout_button)

        self.add_widget(button_layout)

    def confirm_logout(self, instance):
        # Create a confirmation popup
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text="Are you sure you want to logout?", size_hint_y=None, height=40))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10)

        yes_button = Button(text="Yes", on_press=self.logout)
        no_button = Button(text="No", on_press=lambda x: self.popup.dismiss())

        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)
        content.add_widget(button_layout)

        self.popup = Popup(title="Logout Confirmation", content=content, size_hint=(0.8, 0.4))
        self.popup.open()

    def logout(self, instance):
        # Go back to the login screen
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(LoginScreen())

    def post_announcement(self, instance):
        # Create a popup for entering an announcement
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.announcement_input = TextInput(hint_text="Enter Announcement", size_hint=(1, None), height=100)
        content.add_widget(self.announcement_input)

        # Add Submit and Cancel buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=10)

        submit_button = Button(text="Submit", on_press=self.submit_announcement)
        cancel_button = Button(text="Cancel", on_press=lambda x: self.popup.dismiss())
        
        button_layout.add_widget(submit_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(button_layout)

        self.popup = Popup(title="Post Announcement", content=content, size_hint=(0.8, 0.5))
        self.popup.open()

    def submit_announcement(self, instance):
        announcement = self.announcement_input.text

        if announcement:
            # Add the announcement to the data
            data['announcements'].append({
                'department': self.rep_info.get('department_name', 'Unknown Department'),
                'announcement': announcement
            })

            # Save the updated data to the JSON file
            with open('student_data.json', 'w') as f:
                json.dump(data, f, indent=4)

            # Close the popup
            self.popup.dismiss()

            # Show success message
            popup = Popup(title="Success",
                          content=Label(text="Announcement posted successfully!"),
                          size_hint=(None, None), size=(400, 200))
            popup.open()

            # Notify the user about the new announcement
            try:
                notification.notify(
                    title="New Announcement",
                    message=announcement,
                    timeout=10  # Display notification for 10 seconds
                )
            except Exception as e:
                print(f"Failed to send notification: {e}")

        else:
            # Error handling if announcement is empty
            popup = Popup(title="Error",
                          content=Label(text="Announcement cannot be empty!"),
                          size_hint=(None, None), size=(400, 200))
            popup.open()

class RegistrationScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(RegistrationScreen, self).__init__(**kwargs)
        # Placeholder for registration screen
        self.add_widget(Label(text="Registration Screen"))

        # Add gradient background
        
        gradient = Image(source='gradient_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(gradient)

        # Add logo image
        logo = Image(source='icct_logo.png', size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5, 'top': 0.9})
        self.add_widget(logo)

        # Title label
        title_label = Label(text="Register as Department Representative",
                            font_size=28, bold=True,
                            size_hint=(0.8, 0.1),
                            pos_hint={'center_x': 0.5, 'top': 0.8},
                            color=(0, 0, 0, 1))  # Dark text color
        self.add_widget(title_label)

        # Layout for form elements
        form_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(0.8, 0.5), pos_hint={'center_x': 0.5, 'top': 0.65})

        # Department Name input
        self.department_name_input = TextInput(hint_text="Enter Department Name",
                                               multiline=False, size_hint=(1, 0.2),
                                               background_color=(1, 1, 1, 0.7),
                                               padding_y=[10, 10],
                                               foreground_color=(0, 0, 0, 1),
                                               hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.department_name_input)

        # Username input
        self.username_input = TextInput(hint_text="Enter Department Username",
                                        multiline=False, size_hint=(1, 0.2),
                                        background_color=(1, 1, 1, 0.7),
                                        padding_y=[10, 10],
                                        foreground_color=(0, 0, 0, 1),
                                        hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.username_input)

        # Password input
        self.password_input = TextInput(hint_text="Enter Password", password=True,
                                        multiline=False, size_hint=(1, 0.2),
                                        background_color=(1, 1, 1, 0.7),
                                        padding_y=[10, 10],
                                        foreground_color=(0, 0, 0, 1),
                                        hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.password_input)

        # Confirm button
        confirm_button = RoundedButton(text="Confirm Registration", size_hint=(1, None), height=50,
                                       on_press=self.register_rep)
        form_layout.add_widget(confirm_button)

        # Back button
        back_button = RoundedButton(text="Back", size_hint=(1, None), height=50,
                                    on_press=self.back_to_login)
        form_layout.add_widget(back_button)

        # Error message label
        self.error_message = Label(text='', color=(1, 0, 0, 1), size_hint=(1, None), height=30, pos_hint={'center_x': 0.5, 'top': 0.2})
        self.add_widget(self.error_message)

        self.add_widget(form_layout)

    def register_rep(self, instance):
        department_name = self.department_name_input.text
        username = self.username_input.text
        password = hash_password(self.password_input.text)

        # Validate fields
        if department_name and username and password:
            # Add new representative to data
            data['representatives'].append({
                'department_name': department_name,
                'username': username,
                'password': password
            })

            # Save to JSON
            with open('student_data.json', 'w') as f:
                json.dump(data, f, indent=4)

            # Success message
            popup = Popup(title='Registration Successful',
                          content=Label                          (text='You have successfully registered as a Department Representative.'),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            self.back_to_login(None)
        else:
            self.error_message.text = 'Please fill in all fields.'

    def back_to_login(self, instance):
        self.clear_widgets()
        self.add_widget(LoginScreen())

class StudentRegistrationScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(StudentRegistrationScreen, self).__init__(**kwargs)
        # Placeholder for student registration screen
        self.add_widget(Label(text="Student Registration Screen"))

        # Add gradient background
        gradient = Image(source='gradient_bg.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(gradient)

        # Add logo image
        logo = Image(source='icct_logo.png', size_hint=(0.5, 0.3), pos_hint={'center_x': 0.5, 'top': 0.9})
        self.add_widget(logo)

        # Title label
        title_label = Label(text="Register as Student",
                            font_size=28, bold=True,
                            size_hint=(0.8, 0.1),
                            pos_hint={'center_x': 0.5, 'top': 0.8},
                            color=(0, 0, 0, 1))  # Dark text color
        self.add_widget(title_label)

        # Layout for form elements
        form_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(0.8, 0.5), pos_hint={'center_x': 0.5, 'top': 0.65})

        # Name input
        self.name_input = TextInput(hint_text="Enter Full Name",
                                    multiline=False, size_hint=(1, 0.2),
                                    background_color=(1, 1, 1, 0.7),
                                    padding_y=[10, 10],
                                    foreground_color=(0, 0, 0, 1),
                                    hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.name_input)

        # Student number input
        self.student_number_input = TextInput(hint_text="Enter Student Number",
                                              multiline=False, size_hint=(1, 0.2),
                                              background_color=(1, 1, 1, 0.7),
                                              padding_y=[10, 10],
                                              foreground_color=(0, 0, 0, 1),
                                              hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.student_number_input)

         # Add email input field
        self.email_input = TextInput(hint_text="Enter Email",
                                     multiline=False, size_hint=(1, 0.2),
                                     background_color=(1, 1, 1, 0.7),
                                     padding_y=[10, 10],
                                     foreground_color=(0, 0, 0, 1),
                                     hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.email_input)

        # Section input
        self.section_input = TextInput(hint_text="Enter Section",
                                       multiline=False, size_hint=(1, 0.2),
                                       background_color=(1, 1, 1, 0.7),
                                       padding_y=[10, 10],
                                       foreground_color=(0, 0, 0, 1),
                                       hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.section_input)

        # Password input
        self.password_input = TextInput(hint_text="Enter Password", password=True,
                                        multiline=False, size_hint=(1, 0.2),
                                        background_color=(1, 1, 1, 0.7),
                                        padding_y=[10, 10],
                                        foreground_color=(0, 0, 0, 1),
                                        hint_text_color=(0.5, 0.5, 0.5, 1))
        form_layout.add_widget(self.password_input)

        # Confirm button
        confirm_button = RoundedButton(text="Confirm Registration", size_hint=(1, None), height=50,
                                       on_press=self.register_student)
        form_layout.add_widget(confirm_button)

        # Back button
        back_button = RoundedButton(text="Back", size_hint=(1, None), height=50,
                                    on_press=self.back_to_login)
        form_layout.add_widget(back_button)

        # Error message label
        self.error_message = Label(text='', color=(1, 0, 0, 1), size_hint=(1, None), height=30, pos_hint={'center_x': 0.5, 'top': 0.2})
        self.add_widget(self.error_message)

        self.add_widget(form_layout)

    def register_student(self, instance):
        name = self.name_input.text
        student_number = self.student_number_input.text
        section = self.section_input.text
        password = hash_password(self.password_input.text)
        email = self.email_input.text  # Get the email from the email input field

        # Validate fields
        if name and student_number and section and password and email:
            # Add new student to data
            data['students'].append({
                'name': name,
                'student_number': student_number,
                'section': section,
                'password': password,
                'email': email  # Add the email to the student data
            })

            # Save to JSON
            with open('student_data.json', 'w') as f:
                json.dump(data, f, indent=4)

            # Send email notification
            self.send_email_notification(name, email)

            # Success message
            popup = Popup(title='Registration Successful',
                          content=Label(text='You have successfully registered as a student.'),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            self.back_to_login(None)
        else:
            self.error_message.text = 'Please fill in all fields.'

    def send_email_notification(self, name, email):
        # Email configuration
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = 'Registration Successful'

        body = f'Dear {name},\n\nYou have successfully registered as a student.\n\nBest regards,\nICCT College'
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, email, text)
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()

    def back_to_login(self, instance):
        self.clear_widgets()
        self.add_widget(LoginScreen())

class MyApp(App):
    def build(self):
        return LoginScreen()

if __name__ == '__main__':
    MyApp().run()