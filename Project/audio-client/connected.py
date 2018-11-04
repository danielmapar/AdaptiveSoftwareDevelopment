from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.image import Image

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

import os

import speech_recognition as sr

class Connected(Screen):
    microphone_list = []
    listening_is_on = False
    stop_listening = None
    transport = None
    client = None
    app = None

    def on_enter(self, *args):

        transport = RequestsHTTPTransport(
            url='http://localhost:3000/graphql',
            use_json=True
        )

        transport.headers = {'Authorization': 'Bearer ' + self.app.jwt_token}

        client = Client(
            retries=3,
            transport=transport,
            fetch_schema_from_transport=True,
        )

        query = gql("query { me { listenerCommand  } commands { from, to } }")

        try:
            self.app.commands = client.execute(query)
        except Exception as err:
            print(err)
            pass

        pass

    def __init__(self, **kwargs):
        self.name='connected'
        super(Screen,self).__init__(**kwargs)

        self.app = App.get_running_app()

        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        with self.m as source:
            self.r.adjust_for_ambient_noise(source)

        self.microphone_list = sr.Microphone.list_microphone_names()

        layout = BoxLayout(orientation='vertical', size=(Window.size[0],Window.size[1]), pos=(0, 0), size_hint=(None, None))

        dropdown = DropDown()
        for microphone in self.microphone_list:
            btn = Button(text=microphone, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        # create a big main button
        self.dropdown_btn = Button(text=self.microphone_list[0], pos=(0, 0), size_hint = (1, None))
        self.dropdown_btn.bind(on_release=dropdown.open)
        dropdown.bind(on_select=self.on_select_microphone)

        self.loading_img = Image(source = 'images/listening_off.jpeg', allow_stretch=True)

        self.listening_btn = Button(text="Make me listen...", pos=(0, 0), size_hint = (1, None), on_press=self.change_listening_status)
        self.disconnect_btn = Button(text="Disconnect", pos=(0, 0), size_hint = (1, None), on_press=self.disconnect)

        layout.add_widget(self.listening_btn)
        layout.add_widget(self.loading_img)
        layout.add_widget(self.dropdown_btn)
        layout.add_widget(self.disconnect_btn)

        self.add_widget(layout)

    def change_listening_status(self, instance):
        if self.listening_is_on == True:
            self.stop_active_listening()
        else:
            self.start_active_listen()

    def on_select_microphone(self, instance, selected_microphone):
        setattr(self.dropdown_btn, 'text', selected_microphone)

        microphones = self.m.list_microphone_names()
        self.m = sr.Microphone(device_index=microphones.index(selected_microphone))

        if self.stop_listening:
            self.stop_active_listening()

    def listening_callback(self, recognizer, audio):
        print("Listening...")
        try:
            current_command = recognizer.recognize_google(audio)
            if current_command == self.app.commands['me']['listenerCommand']:
                os.system('say Tell me a command!')

            for command in self.app.commands['commands']:
                if current_command == command['from']:
                    os.system('say Command accepted!')
                    print("Send command - TODO")

            print("------")
        except sr.UnknownValueError:
            print("Google could not understand audio")
        except sr.RequestError as e:
            print("Google error; {0}".format(e))

    def start_active_listen(self):
        print("Start Listening!!!")
        self.listening_is_on = True;
        self.listening_btn.text = "Stop listening!"
        self.loading_img.source = 'images/listening_on.png'
        self.loading_img.reload()
        self.stop_listening = self.r.listen_in_background(self.m, self.listening_callback)

    def stop_active_listening(self):
        print("Stopped Listening!!!")
        self.listening_is_on = False;
        self.listening_btn.text = "Make me listen!"
        self.loading_img.source = 'images/listening_off.jpeg'
        self.loading_img.reload()
        self.stop_listening(False)

    def disconnect(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'login'
        self.manager.get_screen('login').resetForm()
