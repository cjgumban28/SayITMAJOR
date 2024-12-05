from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.lang import global_idmap

import requests 
BASE_URL='http://127.0.0.1:8000'
class AddNovelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=15, padding=20)

        # Set background color
        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        
        self.layout.add_widget(Label(text='Add New Novel',font_size=28,color=[0,0,0,1]))

        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Title Input
        self.layout.add_widget(Label(text="Title", font_size='18sp',color=[0,0,0,1], bold=True))
        self.title_input = TextInput(multiline=False, size_hint_y=None, height=40, padding_y=(10, 10), background_color=(1, 1, 1, 1))
        self.layout.add_widget(self.title_input)

        # Description Input
        self.layout.add_widget(Label(text="Description", font_size='18sp',color=[0,0,0,1], bold=True))
        self.description_input = TextInput(multiline=False, size_hint_y=None, height=40, padding_y=(10, 10), background_color=(1, 1, 1, 1))
        self.layout.add_widget(self.description_input)

        # Content Input
        self.layout.add_widget(Label(text="Content", font_size='18sp',color=[0,0,0,1], bold=True))
        self.content_input = TextInput(size_hint_y=None, height=150, padding_y=(10, 10), background_color=(1, 1, 1, 1))
        self.layout.add_widget(self.content_input)

        # Submit Button
        self.submit_btn = Button(
            text="Submit",
            size_hint=(1, None),
            height=50,
            background_color=(0.3, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        self.submit_btn.bind(on_release=self.add_novel)
        self.layout.add_widget(self.submit_btn)

        # Cancel Button
        self.cancel_btn = Button(
            text="Cancel",
            size_hint=(1, None),
            height=50,
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        self.cancel_btn.bind(on_release=self.goBack)
        self.layout.add_widget(self.cancel_btn)

        # Result Label for messages
        self.result_label = Label(size_hint_y=None, height=30, color=(0, 1, 0, 1))
        self.layout.add_widget(self.result_label)

        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def goBack(self, *args):
        self.manager.current = 'home'

    def add_novel(self, instance):
        title = self.title_input.text.strip()
        description = self.description_input.text.strip()
        content = self.content_input.text.strip()

        token = global_idmap["app"].token  # Ensure this is the correct token
        if not token:
            self.result_label.text = "No token found. Please login again."
            return
        
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.post(
                f"{BASE_URL}/novels/",
                json={"title": title, "description": description, "content": content},params={"token":token},
                headers=headers, 
            )
            if response.status_code == 200:
                self.result_label.text = "Novel added successfully"
                self.cancel_btn.text = 'Back'
                self.clear_inputs()
            elif response.status_code == 401:
                self.result_label.text = "Unauthorized. Please login again."
            else:
                self.result_label.text = f"Failed to add novel: {response.text}"
        except requests.exceptions.ConnectionError:
            self.result_label.text = "Cannot connect to server"

    def clear_inputs(self):
        self.title_input.text = ''
        self.description_input.text = ''
        self.content_input.text = ''

class MyApp(App):
    def build(self):
        return AddNovelScreen()

if __name__ == '__main__':
    MyApp().run()
