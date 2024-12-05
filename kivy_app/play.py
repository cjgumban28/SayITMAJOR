from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

class NovelModal(Popup):
    def __init__(self, novel, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Novel: {novel['title']}"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = True

        # Main layout for the modal
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Novel description
        self.layout.add_widget(Label(text=novel['description'], size_hint_y=None, height=100))

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
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

        # Example novels (Replace this with your actual novels data)
        self.novels = [
            {'title': 'Novel 1', 'description': 'This is the first novel.'},
            {'title': 'Novel 2', 'description': 'This is the second novel.'},
            {'title': 'Novel 3', 'description': 'This is the third novel.'},
        ]

        # List of novels
        for novel in self.novels:
            btn = Button(
                text=novel['title'],
                size_hint_y=None,
                height=50,
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1),
                font_size='18sp'
            )
            btn.bind(on_release=lambda instance, n=novel: self.show_novel_modal(n))
            self.layout.add_widget(btn)

        self.add_widget(self.layout)

    def show_novel_modal(self, novel):
        modal = NovelModal(novel)
        modal.open()

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

if __name__ == '__main__':
    MyApp().run()
