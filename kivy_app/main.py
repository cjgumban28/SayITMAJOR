
from kivy.modules.screen import devices,apply_device
apply_device('phone_android_one',.8,'portrait')
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.lang import global_idmap
from kivy.graphics import Color,Rectangle

from screens.home import HomeScreen
from screens.addnovel import AddNovelScreen



BASE_URL = "http://127.0.0.1:8000"  # Replace with your backend URL


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(  **kwargs)
                # Create a BoxLayout
        self.layout = BoxLayout(orientation="vertical", spacing=20, padding=50)
        
        # Set a background color with graphics
        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)

        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Add a title label
        title_label = Label(text="Login",color=[0,0,0,1], font_size='32sp', bold=True, size_hint_y=None, height=50)
        self.layout.add_widget(title_label)

        #spacer
        self.layout.add_widget(Label())
        
        # Username input
        self.layout.add_widget(Label(text="Username", font_size='18sp',color=[0,0,0,1]))
        self.username = TextInput(multiline=False, size_hint_y=None, height=60, 
                                   hint_text="Enter your username", hint_text_color=(0.7, 0.7, 0.7, 1))
        self.layout.add_widget(self.username)

        # Password input
        self.layout.add_widget(Label(text="Password", font_size='18sp',color=[0,0,0,1]))
        self.password = TextInput(multiline=False, password=True, size_hint_y=None, height=60, 
                                   hint_text="Enter your password", hint_text_color=(0.7, 0.7, 0.7, 1))
        self.layout.add_widget(self.password)

        #spacer
        self.layout.add_widget(Label())
        
        # Login button
        self.login_btn = Button(text="Login", size_hint_y=None, height=50,
                                background_color=(0.3, 0.6, 0.8, 1), 
                                color=(1, 1, 1, 1), font_size='18sp')
        self.login_btn.bind(on_release=self.login_user)
        self.layout.add_widget(self.login_btn)

        # Register button
        self.register_btn = Button(text="Register", size_hint_y=None, height=50,
                                   background_color=(0.8, 0.3, 0.3, 1),
                                   color=(1, 1, 1, 1), font_size='18sp')
        self.register_btn.bind(on_release=self.go_to_register)
        self.layout.add_widget(self.register_btn)

        # Error label
        self.error_label = Label(color=(1, 0, 0, 1), size_hint_y=None, height=30)
        self.layout.add_widget(self.error_label)

        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def login_user(self, instance):
        username = self.username.text
        password = self.password.text
        
        try:
            response = requests.post(f"{BASE_URL}/login/?username={username}&password={password}")
            if response.status_code == 200:
                token = response.json()["token"]
                print('got the token from server',token)
                global_idmap["app"].token = token
                self.manager.current = "home"
            else:
                self.error_label.text = "Invalid credentials"
        except requests.exceptions.ConnectionError:
            self.error_label.text = "Cannot connect to server"
    
    def go_to_register(self, instance):
        self.manager.current = "register"


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        
        self.layout.add_widget(Label(text="Username"))
        self.username = TextInput(multiline=False)
        self.layout.add_widget(self.username)
        
        self.layout.add_widget(Label(text="Email"))
        self.email = TextInput(multiline=False)
        self.layout.add_widget(self.email)
        
        self.layout.add_widget(Label(text="Password"))
        self.password = TextInput(multiline=False, password=True)
        self.layout.add_widget(self.password)
        
        self.register_btn = Button(text="Register", size_hint=(1, 0.2))
        self.register_btn.bind(on_release=self.register_user)
        self.layout.add_widget(self.register_btn)
        
        self.result_label = Label(color=(0, 1, 0, 1))
        self.layout.add_widget(self.result_label)
        
        self.back_btn = Button(text="Back to Login", size_hint=(1, 0.2))
        self.back_btn.bind(on_release=self.go_to_login)
        self.layout.add_widget(self.back_btn)
        
        self.add_widget(self.layout)

    def register_user(self, instance):
        username = self.username.text
        email = self.email.text
        password = self.password.text
        
        try:
            response = requests.post(
                f"{BASE_URL}/users/",
                json={"username": username, "email": email, "password": password},
            )
            if response.status_code == 200:
                self.result_label.text = "User registered successfully"
            else:
                self.result_label.text = "Registration failed. Check details."
        except requests.exceptions.ConnectionError:
            self.result_label.text = "Cannot connect to server"

    def go_to_login(self, instance):
        self.manager.current = "login"

import requests
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.app import App

BASE_URL = "http://127.0.0.1:8000"

# class HomeScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

#         self.fetch_btn = Button(text="View All Novels", size_hint=(1, 0.2))
#         self.fetch_btn.bind(on_release=self.fetch_novels)
#         self.layout.add_widget(self.fetch_btn)

#         self.add_novel_btn = Button(text="Add New Novel", size_hint=(1, 0.2))
#         self.add_novel_btn.bind(on_release=self.go_to_add_novel)
#         self.layout.add_widget(self.add_novel_btn)

#         self.result_label = Label()
#         self.layout.add_widget(self.result_label)

#         self.scroll_view = ScrollView()
#         self.novels_list = BoxLayout(orientation="vertical", size_hint_y=None)
#         self.novels_list.bind(minimum_height=self.novels_list.setter("height"))
#         self.scroll_view.add_widget(self.novels_list)
#         self.layout.add_widget(self.scroll_view)

#         self.add_widget(self.layout)

#     def fetch_novels(self, instance):
#         self.novels_list.clear_widgets()
#         try:
#             response = requests.get(f"{BASE_URL}/novels/")
#             if response.status_code == 200:
#                 novels = response.json()
#                 for novel in novels:
#                     btn = Button(
#                         text=f"Title: {novel['title']}\nDescription: {novel['description']}",
#                         size_hint_y=None,
#                         height=100,
#                     )
#                     self.novels_list.add_widget(btn)
#             else:
#                 self.result_label.text = "Failed to fetch novels"
#         except requests.exceptions.ConnectionError:
#             self.result_label.text = "Cannot connect to server"

#     def go_to_add_novel(self, instance):
#         self.manager.current = "add_novel"


# class AddNovelScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

#         self.layout.add_widget(Label(text="Title"))
#         self.title_input = TextInput(multiline=False)
#         self.layout.add_widget(self.title_input)

#         self.layout.add_widget(Label(text="Description"))
#         self.description_input = TextInput(multiline=False)
#         self.layout.add_widget(self.description_input)

#         self.layout.add_widget(Label(text="Content"))
#         self.content_input = TextInput()
#         self.layout.add_widget(self.content_input)

#         self.submit_btn = Button(text="Submit", size_hint=(1, 0.2))
#         self.submit_btn.bind(on_release=self.add_novel)
#         self.layout.add_widget(self.submit_btn)
        
#         self.cancel_btn = Button(text="Cancel", size_hint=(1, 0.2))
#         self.cancel_btn.bind(on_release=self.goBack)
#         self.layout.add_widget(self.cancel_btn)

#         self.result_label = Label(color=(0, 1, 0, 1))
#         self.layout.add_widget(self.result_label)

#         self.add_widget(self.layout)
#     def goBack(self,*args):
#         self.manager.current='home'

#     def add_novel(self, instance):
#         title = self.title_input.text
#         description = self.description_input.text
#         content = self.content_input.text

#         token= global_idmap["app"].token  # Ensure this is the correct token
#         print('sending the token',token)
#         if not token:
#             self.result_label.text = "No token found. Please login again."
#             return
        
#         headers = {"Authorization": f"Bearer {token}"}


#         try:
#             response = requests.post(
#                 f"{BASE_URL}/novels/",
#                 json={"title": title, "description": description, "content": content},params= {"token":token},
#                 headers=headers,
#             )
#             if response.status_code == 200:
#                 self.result_label.text = "Novel added successfully"
#                 self.cancel_btn.text='Back'
#             elif response.status_code == 401:
#                 self.result_label.text = "Unauthorized. Please login again."
#             else:
#                 self.result_label.text = f"Failed to add novel: {response.text}"
#         except requests.exceptions.ConnectionError:
#             self.result_label.text = "Cannot connect to server"



class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(RegisterScreen(name="register"))
        self.add_widget(HomeScreen(name="home"))
        self.add_widget(AddNovelScreen(name="add_novel"))


class NovelApp(App):
    token = None

    def build(self):
        return MyScreenManager()


if __name__ == "__main__":
    NovelApp().run()
