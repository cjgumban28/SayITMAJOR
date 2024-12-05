from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
import requests


BASE_URL = 'http://127.0.0.1:8000'

class IconButton(ButtonBehavior,BoxLayout):
    def __init__(self, icon_src, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (50, 50)  # Width and height of the button

        # Create the icon
        self.icon = Image(source=icon_src, size_hint=(None, None), size=(30, 30))
        self.add_widget(self.icon)

        
        

class NovelModal(Popup):
    def __init__(self, novel, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Novel: {novel['title']}"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = True

        # Main layout for the modal
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Novel description
        self.description_label = Label(text=novel['description'], size_hint_y=None)
        self.description_label.bind(size=self.description_label.setter('size'))  # Bind size to adjust height
        self.description_label.bind(texture_size=self.description_label.setter('size'))  # Set size to texture size
        self.layout.add_widget(self.description_label)

        # ScrollView for the novel content
        self.content_scroll = ScrollView(size_hint=(1, None), size=(self.width, 300))
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        # Novel Content
        self.content_label = Label(text=novel['content'], size_hint_y=None, text_size=(self.width, None))
        self.content_label.bind(height=self.content_label.setter('height'))  # Automatically adjust height
        self.content_layout.add_widget(self.content_label)
        self.content_scroll.add_widget(self.content_layout)

        self.layout.add_widget(self.content_scroll)

        # Comment Input
        self.layout.add_widget(Label(text="Your Comment", font_size='18sp', bold=True))
        self.comment_input = TextInput(multiline=True, size_hint_y=None, height=100)
        self.layout.add_widget(self.comment_input)

        # Like Button
        self.like_btn = Button(
            text="Like",
            size_hint=(1, None),
            height=50,
            background_color=(0.3, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        self.like_btn.bind(on_release=self.like_novel)
        self.layout.add_widget(self.like_btn)

        # Submit Comment Button
        self.submit_comment_btn = Button(
            text="Submit Comment",
            size_hint=(1, None),
            height=50,
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        self.submit_comment_btn.bind(on_release=self.submit_comment)
        self.layout.add_widget(self.submit_comment_btn)

        # Result Label for feedback
        self.result_label = Label(size_hint_y=None, height=30)
        self.layout.add_widget(self.result_label)

        self.add_widget(self.layout)

    def like_novel(self, instance):
        # Logic to like the novel
        self.result_label.text = "You liked this novel!"

    def submit_comment(self, instance):
        comment = self.comment_input.text.strip()
        if comment:
            # Logic to submit the comment (e.g., send to server)
            self.result_label.text = "Comment submitted!"
            self.comment_input.text = ''  # Clear the comment input
        else:
            self.result_label.text = "Please enter a comment before submitting."

            
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set the main layout
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

        # Background color
        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)

        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        self.topBox = BoxLayout(size_hint_y=None, height=60)
        self.layout.add_widget(self.topBox )
        # Title Label
        title_label = Label(text="Welcome to the Novel App",color=(0, 0, 0, 1), font_size='24sp', bold=True, size_hint_y=None, height=50)
        self.topBox.add_widget(title_label)
        self.topBox.add_widget(IconButton(icon_src='./refresh.png',text='',on_release=self.fetch_novels,pos_hint={"center_y":.5}))
        self.topBox.add_widget(IconButton(icon_src='./plus.png',text='',on_release=self.go_to_add_novel,pos_hint={"center_y":.5}))

        # # View All Novels Button
        # self.fetch_btn = Button(
        #     text="View All Novels",
        #     size_hint=(1, None),
        #     height=50,
        #     background_color=(0.3, 0.6, 0.8, 1),
        #     color=(1, 1, 1, 1),
        #     font_size='18sp'
        # )
        # self.fetch_btn.bind(on_release=self.fetch_novels)
        # self.layout.add_widget(self.fetch_btn)

        # # Add New Novel Button
        # self.add_novel_btn = Button(
        #     text="Add New Novel",
        #     size_hint=(1, None),
        #     height=50,
        #     background_color=(0.8, 0.3, 0.3, 1),
        #     color=(1, 1, 1, 1),
        #     font_size='18sp'
        # )
        # self.add_novel_btn.bind(on_release=self.go_to_add_novel)
        # self.layout.add_widget(self.add_novel_btn)

        # Result Label for error messages
        self.result_label = Label(size_hint_y=None, height=30, color=(1, 0, 0, 1))
        self.layout.add_widget(self.result_label)

        # ScrollView for novels list
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.novels_list = BoxLayout(orientation="vertical", size_hint_y=None)
        self.novels_list.bind(minimum_height=self.novels_list.setter("height"))
        self.scroll_view.add_widget(self.novels_list)
        self.layout.add_widget(self.scroll_view)

        self.add_widget(self.layout)
    def on_enter(self):
        self.fetch_novels()
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def fetch_novels(self, instance=None):
        self.novels_list.clear_widgets()
        self.result_label.text = ""  # Clear previous messages
        try:
            response = requests.get(f"{BASE_URL}/novels/")
            if response.status_code == 200:
                novels = response.json()
                for novel in novels:
                    btn = Button(
                        text=f"Title: {novel['title']}\nDescription: {novel['description']}",
                        size_hint_y=None,
                        height=100,
                        background_color=(0.9, 0.9, 0.9, 1),
                        color=(0, 0, 0, 1),
                        font_size='16sp',
                        on_release=lambda x:self.show_novel_modal(novel)
                    )
                    self.novels_list.add_widget(btn)
            else:
                self.result_label.text = "Failed to fetch novels"
        except requests.exceptions.ConnectionError:
            self.result_label.text = "Cannot connect to server"

    def go_to_add_novel(self, instance):
        self.manager.current = "add_novel"
    
    def show_novel_modal(self, novel,*args):
        print(novel)
        modal = NovelModal(novel)
        modal.open()

class MyApp(App):
    def build(self):
        return HomeScreen()

if __name__ == '__main__':
    MyApp().run()
