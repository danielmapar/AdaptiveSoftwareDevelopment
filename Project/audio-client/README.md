# Command Listener

* MacOSX:
  * `brew install portaudio`
    * Necessary for capturing microphone input
  * `brew install automake`


* Linux:
  * `sudo apt install libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg`
  * `sudo apt-get install python-pyaudio python3-pyaudio`
    * Necessary for capturing microphone input

* For all OSs:
  * Install  [PocketSpinx](http://jrmeyer.github.io/asr/2016/01/09/Installing-CMU-Sphinx-on-Ubuntu.html)
  * `pip3 install -r requirements.txt`
  * `python3 speech_live_recognition.py`
