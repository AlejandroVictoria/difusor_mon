import requests
import json
import datetime as dt
import pytz
import os.path
import time
from pygame import mixer

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import texttospeech


months = {
	'1': "enero",
	'2': "febrero",
	'3': "marzo",
	'4': "abril",
	'5': "mayo",
	'6': "junio",
	'7': "julio",
	'8': "agosto",
	'9': "septiembre",
	'10': "octubre",
	'11': "noviembre",
	'12': "diciembre"
	}
	
weekdays = {
	'0': 'Lunes',
	'1': 'Martes',
	'2': 'Miércoles',
	'3': 'Jueves',
	'4': 'Viernes',
	'5': 'Sábado',
	'6': 'Domingo'
}


"""
Date and Time
Section implemented to retrieve data related to local hour and days of
the week.
"""
def time_api(keywords):
	#Return current hour
	return_value = {}
	
	if ('actual' in keywords) & ('reloj' in keywords):
		return_value = dt.datetime.now()
	else:
		return_value = "No pude completar tu petición."

	return return_value


def date_api(keywords):
	#Return actual day
	return_value = {}
	
	if ('actual' in keywords) & ('fecha' in keywords):
		return_value = dt.datetime.now()
		
	else:
		return_value = "No pude completar tu petición."
		
	return return_value


"""
Weather api:
User: Alejandro Victoria
Password: wthr2406_difusor
API Key: b73a47499e984358976760c0033305ea

Current weather:
Campos de interés: sunrise (hora en la que amanece), sunset (hora en la que atardece,
temp (temperatura en °C), weather (icon, description) (contiene una descripción del clima),
UV (indice de luz ultravioleta 0-11+), pop (probabilidad de lluvia).

"""
				
def weather_api(keywords):
	#Retrieve weather information either if it is for current day
	#or for days after.
	
	#Set the endpoint
#	api_key = "502f72b1f937405499b557408756a0e4"
	api_key = "09831ffe864e4ed4b95dde65720ce55e"
	lang = "es"
	#city_id = "3530597"					# CDMX
	city_id = "3529612"				# Ecatepec 
	days = 2
	return_value = {}
	
	url_today = "https://api.weatherbit.io/v2.0/current?"\
				"key={api_key}&"\
				"lang={lang}&"\
				"city_id={city_id}&"\
				"".format(api_key=api_key,lang=lang,city_id=city_id)

	url_forecast = "https://api.weatherbit.io/v2.0/forecast/daily?"\
					"key={api_key}&"\
					"lang={lang}&"\
					"city_id={city_id}&"\
					"days={days}".format(api_key=api_key, lang=lang, city_id=city_id, days=days)

	keys_today = ['datetime', 'sunrise', 'sunset', 'temp', 'timezone', 'uv', 'weather']		
	keys_forecast = ['max_temp', 'min_temp', 'pop', 'sunrise_ts', 'sunset_ts', 'uv', 'valid_date', 'weather']
	
	if ('clima' in keywords) & ('hoy' in keywords):
		resp_today = requests.get(url_today)
		resp_forecast = requests.get(url_forecast)
		
		dict_today = dict(resp_today.json())
		dict_forecast = dict(resp_forecast.json())
		
		print(dict_today)
		print(dict_forecast)
		
		for keys in keys_today:
			return_value[keys] = dict_today['data'][0][keys]
			
		return_value['pop'] = dict_forecast['data'][-1]['pop']
		
		##Convertion of timezone:
		date = return_value['datetime'].split(":")[0]
		sunrise_utc = return_value['sunrise']
		sunset_utc = return_value['sunset']
		tz = return_value['timezone']
		
		date_obj = dt.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo= pytz.timezone(tz))
		sunrise_date = dt.datetime.strptime(date + " " + sunrise_utc, "%Y-%m-%d %H:%M").replace(tzinfo= pytz.timezone('UTC'))
		sunset_date = dt.datetime.strptime(date + " " + sunset_utc, "%Y-%m-%d %H:%M").replace(tzinfo= pytz.timezone('UTC'))

	elif ('clima' in keywords) & ('mañana' in keywords):
		resp_forecast = requests.get(url_forecast)
		dict_forecast = dict(resp_forecast.json())
		print("DEBUG: dict_forecast:", dict_forecast)
		data_forecast = dict_forecast['data'][-1]
		
		return_value['timezone'] = dict_forecast['timezone']
		
		for keys in keys_forecast:
			return_value[keys] = data_forecast[keys]
		
		##['max_temp', 'min_temp', 'pop', 'sunrise_ts', 'sunset_ts', 'uv', 'valid_date', 'weather']
		##Convertion of timezone:
		date = return_value['valid_date']
		sunrise_utc = return_value['sunrise_ts']
		sunset_utc = return_value['sunset_ts']
		tz = return_value['timezone']
		
		date_obj = dt.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo= pytz.timezone(tz))
		sunrise_date = dt.datetime.fromtimestamp(sunrise_utc, pytz.timezone('UTC'))
		sunset_date = dt.datetime.fromtimestamp(sunrise_utc, pytz.timezone('UTC'))


	sunrise_mxtz = sunrise_date.astimezone(pytz.timezone(return_value['timezone']))
	sunset_mxtz = sunset_date.astimezone(pytz.timezone(return_value['timezone']))
	
	return_value['datetime'] = date_obj
	return_value['sunrise'] = sunrise_mxtz
	return_value['sunset'] = sunset_mxtz

	print("DEBBUG: return weather data:", return_value)
	return return_value
	

"""
ts = datetime.datetime.fromtimestamp(1717826460, pytz.timezone('UTC'))
>>> ts
datetime.datetime(2024, 6, 8, 6, 1, tzinfo=<UTC>)
>>> new_ts = ts.astimezone(pytz.timezone('America/Mexico_City'))
>>> new_ts
datetime.datetime(2024, 6, 8, 0, 1, tzinfo=<DstTzInfo 'America/Mexico_City' CST-1 day, 18:00:00 STD>)

"""
"""
Agenda
Section implemented to connect with the Google Calendar API to generate
appointments, events, alerts, etc. 

api_key_gc = "AIzaSyA6BH-_v0rUVcF1eer0eQOjnsQmObFOueo"
"""

SCOPES = [
	"https://www.googleapis.com/auth/calendar.readonly",
	"https://www.googleapis.com/auth/calendar"
		]
		

def google_authentication():
	"""
	Authentication of user and credentials. Return an object with credentials.
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			try:
				creds.refresh(Request())
			except:
				if os.path.exists('token.json'):
					os.remove('token.json')
				
				flow = InstalledAppFlow.from_client_secrets_file(
				"credentials.json",
				scopes= SCOPES
				)
				
				creds = flow.run_local_server(port=0)
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				"credentials.json",
				scopes= SCOPES
				)
				
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open("token.json", "w") as token:
			token.write(creds.to_json())
			
	return creds
	

def google_create_events(creds, data):
	return_value = None
	reminder_data = data['datos_recordatorio']
	
	if reminder_data['all_day_event']:
		start_date = {
			'date': str(reminder_data['event_date'].strftime('%Y-%m-%d')),
			'timeZone': 'America/Mexico_City'
			}
		#end_delta = dt.timedelta(days=1)
		#end = reminder_data['event_date'] + end_delta
		end_date = {
			'date': str(reminder_data['event_date'].strftime('%Y-%m-%d')),
			'timeZone': 'America/Mexico_City'
			}
	else:
		start_date = {
			'dateTime': str(reminder_data['event_date'].isoformat()),
			'timeZone': 'America/Mexico_City'
			}
		end_delta = dt.timedelta(hours=1)
		end = reminder_data['event_date'] + end_delta
		end_date = {
			'dateTime': str(end.isoformat()),
			'timeZone': 'America/Mexico_City'
			}
			
	event = {
	'summary': reminder_data['event_description'],
	'location': '',
	'description': reminder_data['event_description'],
	'start': start_date,
	'end': end_date,
	'reminders': {
		'useDefault': False,
		'overrides': [
			{
				'method': 'popup',
				'minutes': 30
				},
			{
				'method': 'popup',
				'minutes': 90
				},
			],
		},
	}
	
	try:
		service = build("calendar", "v3", credentials=creds)
		
		# Call the Calendar API
		now = dt.datetime.utcnow().isoformat() + "Z" # 'Z' indicates UTC time

		event = service.events().insert(calendarId='primary', body=event).execute()
		print('Event created: {e}'.format(e=event.get('htmlLink')))

		return_value = event
		
	except HttpError as error:
		print(f'An error occurred: {error}')
		return_value = error
		
	return return_value
				
def reminders_api(data):
	key_words = data['palabras_clave']
	
	if 'hoy' in key_words:
		events_data = google_retrieve(creds, 'hoy')
	elif 'semana' in key_words:
		events_data = google_retrieve(creds, 'semana')
	else:
		events_data = google_retrieve(creds, 'hoy')
	
	return events_data
	
def google_retrieve(creds, day):
	""""""
	return_data = []
	
	#Preparing range dates to retrieve events
	now_time = dt.datetime.now()
	
	if day == "hoy":
		if now_time.hour > 21:
			delta = dt.timedelta(days=1)
		else:
			delta = dt.timedelta(days=0)
	elif day == "semana":
		delta_day = 6 - now_time.weekday()
		if delta_day == 1:
			delta = dt.timedelta(days=7)
		else:
			delta = dt.timedelta(days=delta_day)
	
	time_max = now_time + delta
	time_max = time_max.replace(hour=23,minute=59,second=59,microsecond=0)
		
	#Preparing date values according to google requirements
	now = now_time.isoformat() + 'Z' # 'Z' indicates UTC time
	time_max = time_max.isoformat() + 'Z' # 'Z' indicates UTC time
	
	#Retrieving data from google api
	try:
		service = build("calendar", "v3", credentials=creds)
		
		# Call the Calendar API
		
		print("Getting the upcoming 10 events")
		events_result = (
			service.events()
			.list(
				calendarId="primary",
				timeMin=now,
				timeMax=time_max,
				maxResults=10,
				singleEvents=True,
				orderBy="startTime",
			)
			.execute()
		)
		events = events_result.get("items", [])
		
		if not events:
			return_data = "No tienes eventos pendientes."
		else:
			return_data = events
			"""			
			# Prints the start and name of the next 10 events
			for event in events:
				start = event["start"].get("dateTime", event["start"].get("date"))
				print(start, event["summary"])
			"""		
	except HttpError as error:
		print(f'An error occurred: {error}')
		return_data = "No pude completar tu petición."
	
	return return_data
	
	
def preparing_data_event(data):
	reminder_data = data['datos_recordatorio']
	date = reminder_data['event_date']
	time = reminder_data['event_time']
	description = reminder_data['event_description']
	#duration = reminder_data['event_duration']
	duration = "1 hora"
	current_date = dt.datetime.now()
	
	#defining date
	try:
		#Setting reminder date with format 'dd-mm'.
		date_day,date_month = date['date'].split('-')
		
		if date_month.isalpha():
			for key in months.keys():
				date_month = key if date_month.lower() == months[key] else date_month
	
		new_reminder_date = current_date.replace(day= int(date_day), month= int(date_month))

	except:
	#if date['date'] == None:
		"""
		cuando no hay una fecha definida en forma 'mm-dd' se usa esta porción de código
		para contar de qué fecha se está hablando (cuando se define una fecha como
		'el jueves dentro de 15 días', 'el miércoles en dos semanas', etc.) y se crea
		un objeto datetime con esa información.
		"""
		
		weekday = date['weekday']
		week = date['week']
		
		#Changing weekday ('jueves', 'viernes', 'sábado', etc) to datetime format ('0', '1', '2', etc.).
		num_weekday = ""
		if weekday == 'mañana':
			week = 0
			if current_date.weekday() == 6:
				num_weekday = 0
			else:
				num_weekday = current_date.weekday() + 1
		else:
			for key in weekdays.keys():
				if weekdays[key].lower() == weekday:
					num_weekday = key
		
		print("num_weekday", num_weekday)
		num_weekday = int(num_weekday)
		condition = False
		days_count = 0
		current_weekday = current_date.weekday()

		#Counting days between current day and day stablished on command (weekday and week values).
		for i in range(0, week + 1):
			for j in range(0, 7):
				if (i == 0) & (j == current_weekday):
					condition = True
				elif (i == week) & (j == num_weekday):
					condition = False
				
				if condition:
					days_count += 1
					
		#Setting new reminder date
		reminder_days = dt.timedelta(days=days_count)
		new_reminder_date = current_date + reminder_days
		
		weekd = weekdays[str(new_reminder_date.weekday())]
		print("El recordatorio quedó programado para el día {day} {date}".format(day=weekd, date=new_reminder_date))
	#else:

	"""
	Iniciar stream...
Starting...
Detener stream...Modo escuchar palabra de activación
Modo escuchar comando
Texto de entrada: crea un recordatorio
response_json: {'palabras_clave': ['crear', 'recordatorio', 'gestión', 'tiempo', 'organización'], 'capacidad': False}
selector:  (0.4, 'agenda')
selector: agenda
creando respuesta...
{'palabras_clave': ['crear', 'recordatorio', 'gestión', 'tiempo', 'organización'], 'capacidad': False, 'selector': 'agenda', 'respuesta_api': 'Muy bien, sólo necesito más información sobre elrecordatorio que necesitas...', 'respuesta_texto': 'Muy bien, sólo necesito más información sobre elrecordatorio que necesitas...'}
Modo escuchar comando
Texto de entrada: el

 {
	'palabras_clave': ['crear', 'recordatorio', 'gestión', 'tiempo', 'organización'], 
	'capacidad': False,
	'selector': 'agenda',
	'respuesta_api': 'Muy bien, sólo necesito más información sobre elrecordatorio que necesitas...',
	'respuesta_texto': 'Muy bien, sólo necesito más información sobre elrecordatorio que necesitas...',
	'datos_recordatorio': {
		'event_date': {'date': 'mañana', 'weekday': 'mañana', 'week': 0},
		'event_time': '00:00',
		'event_description': 'no se proporcionó información específica para describir el evento.',
		'event_duration': '1 hora'
		}
 }
mañana

	"""
	#Setting reminder hour
	all_day_event = True
	
	if time != None:
		if ":" in time:
			hours,minutes = time.split(':')
			new_reminder_date = new_reminder_date.replace(hour= int(hours), minute= int(minutes), second= 0, microsecond= 0)
			all_day_event = False
		else:
			new_reminder_date = new_reminder_date.replace(hour= 0, minute= 0, second= 0, microsecond= 0)
	else:
		new_reminder_date = new_reminder_date.replace(hour= 0, minute= 0, second= 0, microsecond= 0)
	
	#print("El recordatorio se configuró para el día:", new_reminder_date)
	data['datos_recordatorio'] = {
		'event_date': new_reminder_date,
		'event_description': description,
		'all_day_event': all_day_event
		}
	return data

def agenda_api(data):
	"""
	Function created to communicate with google calendar in order to
	create, retrieve, edit and deleted events on calendar
	"""
	return_value = {}
	keys = data.keys()
	if 'datos_recordatorio' in keys:
		data_event = preparing_data_event(data)
		return_value = google_create_events(creds, data_event)
	else:
		return_value = {"text": "Muy bien, sólo necesito más información sobre el"\
			"recordatorio que necesitas...",
						"avoid_creating_text": True}

	time.sleep(1)
	return return_value
	

def tts_api(text_input):
	# Set the text input to be synthesized
	synthesis_input = texttospeech.SynthesisInput(
			text=text_input
		)

	#Build the voice request, select the language code ("en-US") and the ssml
	#voice gender ("neutral")
	voice = texttospeech.VoiceSelectionParams(
			language_code= "es-US",
			ssml_gender= texttospeech.SsmlVoiceGender.FEMALE
		)

	#Select the type of audio file you want returned
	audio_config = texttospeech.AudioConfig(
			audio_encoding= texttospeech.AudioEncoding.MP3
		)
		
	#Perform the text-to-speech request on the text input with the selected
	#voice parameters and audio file type.
	response = client_tts.synthesize_speech(
			input=synthesis_input, voice=voice, audio_config=audio_config
		)

	#The response's audio_content is binary:
	with open("sound_effects/response_audio.mp3", "wb") as out:
		#Write the response to the output file.
		out.write(response.audio_content)
		print("Audio content written")
	

def sound_play(option):
	select_audio = {
		'0': 'sound_effects/response_audio.mp3',
		'1': 'sound_effects/alert_01.mp3',
		'2': 'sound_effects/alert_02.mp3',
		'3': 'sound_effects/alert_03.mp3',
		'4': 'sound_effects/wakesound.mp3'
	}
	
	mixer.init()
	mixer.music.load(select_audio[option])
	mixer.music.play()
	
	while mixer.music.get_busy() == True:
		continue
		
sound_play("1")	
#Initializating google authorizations:
print("Inicializando Google Services...")
creds = google_authentication()
print("Inicializando Google Text-to-speech")
client_tts = texttospeech.TextToSpeechClient()
print("Cargado correctamente")
print("Inicializando recursos")
time.sleep(10)

#print(json.dumps(response_json_pre, indent=2))
