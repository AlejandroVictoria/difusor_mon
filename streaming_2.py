from queue import Queue
from threading import Thread
import io
import numpy as np
import time

import pyaudio
import subprocess
import json
from vosk import Model, KaldiRecognizer

from apis_test import sound_play
from q_classification import analyze_text, setting_reminder



'''Seccion dedicada a la creación de hilos que se encargaran de la
inicialización de la grabación del micrófono en segundo plano.'''

text_processed = Queue()												#Variable que guarda el texto procesado
messages = Queue()														#Variable que mantiene el stream de audio (descartable)
activate_mode = Queue()													#Variable que mantiene el stream de audio (Vacío: 1 segundo, No vacío: 5 segundos)
recordings = Queue()													
recording_command = Queue()
stream_while = Queue()													
mode = Queue()															#Variable que mantiene el modo Escuchar palabra de activación o Escuchar comando
api_key = "sk-proj-SxiYz9RLIHRZEhahLd9xT3BlbkFJLbA5NrQ28EYGgnMQMsiE"
#api_key = "sk-proj-SxiYz9RLIHRZEhahLd9xT3BlbkFJLbA5NrQ28EYGgnMQMsee"
#audio = AudioSegment.from_file("audio.wav", format="wav")


output = []

def start_recording():
	messages.put(True)
	stream_while.put(True)
	activate_mode.put(True)
	
	print("Starting...")
	record = Thread(target = record_microphone)
	record.start()
	
	transcribe = Thread(target = speech_recognition, args = (output,))
	transcribe.start()
	
	listening = Thread(target = assistant_listening)
	listening.start()
	
	return [record, transcribe, listening]
	
def stop_recording(threads):
	stream_while.get()
	messages.get()
	activate_mode.get()
	
	while True:
		th_alive = 0
		
		for th in threads:
			if th.is_alive():
				th_alive += 1
				#print(str(th.name) + ": " + str(th.is_alive()))
		
		#print(th_alive)
		if th_alive > 0:
			if activate_mode.empty():
				activate_mode.put(True)
			else:
				activate_mode.get()
		else:
			break
		
		time.sleep(1)

	print("Stopped...")

'''Sección que muestra la función que se encargará de configurar y
grabar sonidos desde el micrófono.'''

CHANNELS = 1
FRAME_RATE = 48000
ACTIVATION_RECORD = 1.5
COMMAND_RECORD = 6
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_SIZE = 2
DEVICE_INDEX = 2

def record_microphone(chunk = 1024):
	p = pyaudio.PyAudio()
	
	stream = p.open(format = AUDIO_FORMAT,
					channels = CHANNELS,
					rate = FRAME_RATE,
					input = True,
					input_device_index = DEVICE_INDEX,
					frames_per_buffer = chunk
				)
				
	frames = []
	while not stream_while.empty():
		time.sleep(1)
		if mode.empty():
			print("Modo escuchar palabra de activación")
			sound_play("3")
			time.sleep(1)
			while not activate_mode.empty():
				data = stream.read(chunk, exception_on_overflow=False)
				frames.append(data)
				if len(frames) >= (FRAME_RATE * ACTIVATION_RECORD / chunk):
					recordings.put(frames.copy())
					frames = []
		else:
			sound_play("4")
			time.sleep(1)
			print("Modo escuchar comando")
			while activate_mode.empty():
				data = stream.read(chunk, exception_on_overflow=False)
				frames.append(data)
				if len(frames) >= (FRAME_RATE * COMMAND_RECORD / chunk):
					recordings.put(frames.copy())
					frames = []
					
			
	stream.stop_stream()
	stream.close()
	p.terminate()
	

'''Sección donde se construye la función que se encargará del
reconocimiento de voz y transcripción a texto'''

model = Model(model_name = 'vosk-model-small-es-0.42')
rec = KaldiRecognizer(model, FRAME_RATE)
rec.SetWords(True)

def speech_recognition(output):   
	while not messages.empty():
		frames = recordings.get()
		rec.AcceptWaveform(b''.join(frames))
		result = rec.Result()
		text = json.loads(result)["text"]
		text_processed.put(text)

'''Sección donde se desarrolla la función que identificará a la
palabra de activación'''
def assistant_listening():
	i = 0
	cont_value = False
	
	while not messages.empty():
		text = text_processed.get()	
		
		if not activate_mode.empty():
			if text.lower() == "eva":
				activate_mode.get()
				mode.put(True)
		else:
			if not text == "":
				print("Texto de entrada:", text)
				#try:
				if cont_value:
					cont_value = setting_reminder(text)
				else:
					cont_value = analyze_text(text)

				#except Exception as err:
				#	print("Hubo un problema: {error}".format(error=err))
				#	cont_value = False

				if cont_value:
					activate_mode.put(True)
					mode.get()
					time.sleep(0.5)
					activate_mode.get()
					mode.put(True)
				else:
					activate_mode.put(True)
					mode.get()

				
"""
openai devolvió el siguiente mensaje:

raise self._make_status_error_from_response(err.response) from None
openai.RateLimitError: Error code: 429 - {'error': {'message': 'You exceeded your current quota, 
please check your plan and billing details. For more information on this error, read the docs: 
https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 
'param': None, 'code': 'insufficient_quota'}}

Según un foro, se tiene que dar de alta un método de pago e intentar de
nuevo, creando una nueva api key...
"""

##Poniendo a prueba
print("Cargando últimos recursos...")
time.sleep(2)
##sound_play("1")			La función se movió al archivo apis_test.py para que se ejecute al inicio de la carga de todo

print("Bienvenido...")
threading = start_recording()

input("Detener stream...\n")
stop_recording(threading)
