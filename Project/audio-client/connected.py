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
import time
import threading
from threading import Thread

import speech_recognition as sr

class Connected(Screen):
    microphone_list = []
    listening_is_on = False
    transport = None
    client = None
    app = None
    audio_thread = None
    kill_mic_thread = None
    transport = None
    client = None

    def on_enter(self, *args):

        self.kill_mic_thread = threading.Event()

        self.transport = RequestsHTTPTransport(
            url='http://localhost:3000/graphql',
            use_json=True
        )

        self.transport.headers = {'Authorization': 'Bearer ' + self.app.jwt_token}

        self.client = Client(
            retries=3,
            transport=self.transport,
            fetch_schema_from_transport=True,
        )

        query = gql("query { me { listenerCommand  } commands { from, to } }")

        try:
            self.app.commands = self.client.execute(query)
        except Exception as err:
            print(err)

    def __init__(self, **kwargs):
        self.name='connected'
        super(Screen,self).__init__(**kwargs)

        self.app = App.get_running_app()

        self.r = sr.Recognizer()
        self.m = sr.Microphone()

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

        if self.audio_thread:
            self.stop_active_listening()

        microphones = self.m.list_microphone_names()
        self.m = sr.Microphone(device_index=microphones.index(selected_microphone))


    def listen_in_background(self, microphone, recognizer, data, stop_event):
        while not stop_event.wait(1):
            print("-> Waiting control command!!!")
            with microphone as source:
                audio = recognizer.listen(source)

            print("-> Checking control command!!!")
            try:
                call_command = recognizer.recognize_google(audio)
                print(call_command)
                if call_command == data['me']['listenerCommand']:
                    os.system('say Tell me a command!')
                    print(data['commands'])
                    print("-> Waiting command!!!")
                    with microphone as source:
                        audio = recognizer.listen(source)
                    exec_command = recognizer.recognize_google(audio)
                    print("-> Checking command!!!")
                    for command in data['commands']:
                        print(exec_command)
                        print(command['from'])
                        if exec_command == command['from']:
                            os.system('say Command accepted!')
                            mutation = gql("mutation { sendCommand(fromCommand: \"" + exec_command +"\") }")
                            try:
                                self.client.execute(mutation)
                                os.system('say Command executed!')
                            except Exception as err:
                                print(err)

                print("------")
            except sr.UnknownValueError:
                print("Google could not understand audio")
            except sr.RequestError as e:
                print("Google error; {0}".format(e))
            except Exception as e:
                print("General error; {0}".format(e))

    def start_active_listen(self):
        print("Start Listening!!!")
        self.listening_is_on = True;
        self.listening_btn.text = "Stop listening!"
        self.loading_img.source = 'images/listening_on.png'
        self.loading_img.reload()
        self.audio_thread = Thread(target = self.listen_in_background, args=(self.m, self.r, self.app.commands, self.kill_mic_thread))
        self.audio_thread.start()

    def stop_active_listening(self):
        print("Stopped Listening!!!")
        self.listening_is_on = False;
        self.listening_btn.text = "Make me listen!"
        self.loading_img.source = 'images/listening_off.jpeg'
        self.loading_img.reload()
        self.kill_mic_thread.set()
        self.audio_thread.join()

    def disconnect(self, instance):
        self.stop_active_listening()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'login'
        self.manager.get_screen('login').resetForm()
