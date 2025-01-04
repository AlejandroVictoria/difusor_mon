"""
Este script está dedicado a la clasificación de las preguntas hechas
para determinar qué función deberá ejecutarse.
"""
import openai
from openai import OpenAIError
import sounddevice as sd
import soundfile as sf
import json

from calculate_topic import calculate_action
from apis_test import (
	agenda_api,
	time_api,
	date_api,
	weather_api,
	reminders_api,
	tts_api,
	sound_play
)

import time
import datetime as dt
import pytz

api_key = "sk-proj-SxiYz9RLIHRZEhahLd9xT3BlbkFJLbA5NrQ28EYGgnMQMsiE"
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

"""Seccion donde se desarrollan las funciones que se comunicarán con 
la api de openai"""
def setup_openai_client(api_key):
	return openai.OpenAI(api_key = api_key)
		
def fetch_ai_response(client, input_text):
	messages = [{"role": "user", "content": input_text}]
	error = ""
	response = []
	
	try:
		response = client.chat.completions.create(
			#model="gpt-3.5-turbo-1106",
			model="gpt-4-turbo",
			messages=messages
		)
		
	except OpenAIError as e:
		"""EJEMPLO DE MENSAJE DE ERROR:
		
		Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-proj-********************************************Msee.
			You can find your API key at https://platform.openai.com/account/api-keys.',
			'type': 'invalid_request_error',
			'param': None,
			'code': 'invalid_api_key'}}

		"""
		print("mensaje:",e)
		error = e
		pass

	return response,error


"""def creating_voice_response(response_text):
	audio_openai = client.audio.speech.create(
			model="tts-1",
			voice="nova",
			input=response_text
			)

	audio_openai.stream_to_file("response_audio.wav")
	
	audio_file,sr_file = sf.read("./response_audio.wav")
	sd.play(audio_file, sr_file)
	sd.wait()
"""


def creating_text_response(data):
	return_value = ""
	value = data['respuesta_api']
	selector = data['selector']
	capacity = data['capacidad']
	if ('No pude completar tu petición.' == value) | (capacity):
		return_value = value
	else:
		if 'time' == selector:			
			hour = value.hour - 12 if value.hour > 12 else value.hour
			str_sentence = "Son las" if hour != 1 else "Es la"
			if (value.hour > 12) & (value.hour < 19):
				ampm = "de la tarde"
			elif (value.hour > 19) & (value.hour < 23):
				ampm = "de la noche"
			else:
				ampm = "de la mañana"
			
			return_value = "{val} {hour} con {minute} minutos {value_2}"\
							"".format(val= str_sentence, hour= hour, minute= value.minute, value_2= ampm)
		elif 'date' == selector:
			date = data['respuesta_api']
			week_day = date.weekday()
			month_num = date.month
			return_value = "El día de hoy es {weekday}, {day} de {month} de {year}"\
							"".format(weekday=weekdays[str(week_day)],
								day=date.day,
								month=months[str(month_num)],
								year=date.year
								)
			
		elif 'weather' == selector:
			weather = data['respuesta_api']
			print("DEBBUG: weather:", weather)
			if 'hoy' in data['palabras_clave']:
				w_desc = weather['weather']['description']
				temp = weather['temp']
				uv = weather['uv']
				uv_suggest = "es un índice alto, por lo que se recomienda"\
					"evitar activades al aire libre sin el uso de bloqueador."\
					"" if uv > 11 else "" 
				pop = weather['pop']
				
				return_value = "En este momento el clima es {weather_description},"\
								"tenemos una temperatura de {temp}°C con un índice UV de {uv} {uv_suggest}"\
								"y una probabilidad de lluvia del {pop}%"\
								"".format(weather_description=w_desc,
								temp=temp,
								uv=uv,
								uv_suggest=uv_suggest,
								pop=pop
								)
			else:
				w_desc = weather['weather']['description'].lower()
				temp_min = weather['min_temp']
				temp_max = weather['max_temp']
				uv = weather['uv']
				uv_suggest = "es un índice alto, por lo que se recomienda "\
					"evitar activades al aire libre sin el uso de bloqueador."\
					"" if uv > 11 else "" 
				pop = weather['pop']
				weekday_weather = weather['datetime']
				weekday_weather = weekdays[str(weekday_weather.weekday())]
				
				return_value = "Para el día de mañana, {weekday}, se espera un día"\
								" {weather_description} con una temperatura mínima "\
								"de {min_temp}°C y una máxima de {max_temp}°C."\
								" El índice de luz ultravioleta se estima en {uv} puntos. "\
								"{uv_suggestion}. Y una probabilidad de lluvia del {pop}%."\
								"".format(
									weekday= weekday_weather,
									weather_description=w_desc,
									min_temp=temp_min,
									max_temp=temp_max,
									uv=uv,
									uv_suggestion=uv_suggest,
									pop=pop
								)
							
		elif 'agenda' == selector:
			"""
			Falta crear una respuesta por parte del asistente, tanto para el evento
			creado, como para los eventos recuperados.
			"""
			"""
			event_sentence = Se creó el recordatorio {evento}
			day_sentence = para el día {weekday} {day} de {month}
			time_sentence = a las {hora} de la {mañana-tarde-noche}
			"""
			data_api = data['respuesta_api']
			
			if not 'avoid_creating_text' in data_api.keys():
				event_sentence, day_sentence, time_sentence = "", "", ""
				#Definiendo event_sentence
				event = data['respuesta_api']['description']
				event_sentence = "Se creó el recordatorio '{val_1}' ".format(val_1= event)
				
				#Definiendo day_sentence
				event_data = data['datos_recordatorio']
				
				if 'dateTime' in data['respuesta_api']['start']:
					date_time = data['respuesta_api']['start']['dateTime']
					date_obj = dt.datetime.fromisoformat(date_time)
					
					tz = data['respuesta_api']['start']['timeZone']
					tz = pytz.timezone(tz)
					date_obj = date_obj.replace(tzinfo= tz)
					
					hour = date_obj.hour - 12 if date_obj.hour > 12 else date_obj.hour
					sentence_1 = "a las" if hour != 1 else "a la"
					if (date_obj.hour >= 12) & (date_obj.hour < 19):
						ampm = "de la tarde"
					elif (date_obj.hour >= 19) & (date_obj.hour < 24):
						ampm = "de la noche"
					else:
						ampm = "de la mañana"
					
					time_sentence = " {sentence_1} {hours}:{minutes} {ampm}"\
						"".format(sentence_1= sentence_1, hours= date_obj.hour, minutes= date_obj.minute, ampm= ampm)
				else:
					date_time = data['respuesta_api']['start']['date']
					date_obj = dt.datetime.fromisoformat(date_time)
				
				day = date_obj.day
				weekday = weekdays[str(date_obj.weekday())]
				month = months[str(date_obj.month)]
				
				day_sentence = " para el día {weekday} {day} de {month}".format(weekday=weekday, day=day, month=month)
					
				return_value = event_sentence + day_sentence + time_sentence + "."

			else:
				return_value = data_api['text']
		elif 'reminders':
			print("creating_data() - reminders:\n")
			events_data = data['respuesta_api']
			
			print("DEBBUG: events_data:", events_data)
			
			if not 'str' in str(type(events_data)):
				event_length = len(events_data)
				count_event = 1
				time_sentence = ""
				sentence = ""
				
				if 'hoy' in data['palabras_clave']:
					day_request = 'hoy'
					
					if event_length == 1:
						text_events = "El día de hoy tienes 1 pendiente:\n"
					else:
						text_events = "El día de hoy tienes {events} pendientes:\n".format(events= str(event_length))
				else:
					day_request = 'semana'
					if event_length == 1:
						text_events = "Esta semana tienes 1 pendiente:\n"
					else:
						text_events = "Esta semana tienes {events} pendientes:\n".format(events= str(event_length))
				
				for events in events_data:
					"""
					Ejemplo de respuesta:
					"
							- El {día de la semana} {día} a las {hora} de la {momento del día} tienes que {evento}.
							- ...
							- ...
							
						Esos serían tus pendientes de {hoy o la semana}.
					"
					"""
					
					event = events['summary']
					
					date_start = events["start"].get("dateTime", events["start"].get("date"))
					
					date_obj = dt.datetime.fromisoformat(date_start)
					week_day = weekdays[str(date_obj.weekday())]
					
					if 'dateTime' in events['start'].keys():
						tz = events['start']['timeZone']
						tz = pytz.timezone(tz)
						date_obj = date_obj.replace(tzinfo= tz)
						
						hour = date_obj.hour - 12 if date_obj.hour > 12 else date_obj.hour
						sentence_1 = "a las" if hour != 1 else "a la"
						
						if (date_obj.hour >= 12) & (date_obj.hour < 19):
							ampm = "de la tarde"
						elif (date_obj.hour >= 19) & (date_obj.hour < 24):
							ampm = "de la noche"
						else:
							ampm = "de la mañana"
						
						time_sentence = " {sentence_1} {hours}:{minutes} {ampm}"\
							"".format(sentence_1= sentence_1,
									hours= date_obj.hour,
									minutes= date_obj.minute,
									ampm= ampm
									)
					
					if day_request == 'hoy':
						sentence = sentence + "- {time_sentence} tienes que {event}.\n"\
							"".format(
								time_sentence= time_sentence.capitalize(),
								event=event
								)
					
					else:
						sentence = sentence + "- El {day_week} {day}{time_sentence} tienes programado '{event}'.\n"\
							"".format(
							day_week=week_day,
							day= date_obj.day,
							time_sentence= time_sentence,
							event= event
							)
				
				return_value = "{texto} {sentence}Esos serían los pendientes {day_request}."\
								"".format(
									texto= text_events,
									sentence= sentence,
									day_request= "del día." if day_request=="hoy" else "de la semana."
									)
			else:
				return_value = events_data
		else:
			return_value = data['respuesta_api' ]
	
	print("\nDEBBUG: return_value:", return_value)
	
	return return_value
	

def creating_voice_response(text):
	tts_api(text)
	sound_play('0')
	
  
def analyze_text(text):
	continue_condition = False
	
	prompt = "Entrega un objeto de tipo json, con dos campos, el primero:"\
				"palabras_clave, donde indicarás en 5 palabras clave la"\
				"intención de la pregunta: {text}, y el segundo campo:"\
				"capacidad, indicando si puedes "\
				"realizar sin ayuda de herramientas externas la actividad"\
				"solicitada, respondiendo True o False".format(text=text)
	
	response,error = fetch_ai_response(client, prompt)
		
	if error == "":
		response_text = response.choices[0].message.content
	
		index_curly_open = response_text.find("{")
		index_curly_close = response_text.find("}")
		
		pre_json = response_text[index_curly_open:index_curly_close + 1].replace("\n","")
		json_data = json.loads(pre_json.lower())
		dict_resp = dict(json_data)
		
		try:
			capability = dict_resp['capacidad']
		
			if capability:
				dict_resp['pregunta_original'] = text
		
		except:
			pass
			
		print("response_json:", dict_resp)

		dict_resp['respuesta_api'] = select_function(dict_resp)
		
		#print(dict_resp)
		print("creando respuesta...")
		dict_resp['respuesta_texto'] = creating_text_response(dict_resp)
		
		print(dict_resp)
		creating_voice_response(dict_resp['respuesta_texto'])
		
	else:
	 	print("response:", response)
	 	
	if (dict_resp['selector'] == 'agenda') | (dict_resp['selector'] == 'alarma'):
		continue_condition = True
		
		#saving dict_resp on json file
		json_object = json.dumps(dict_resp, indent=2)
		
		with open('data_response.json', 'w') as file_out:
			file_out.write(json_object)

	return continue_condition
	
def select_function(dict_with_data):
	"""Esta función sirve para definir qué tipo de funcionalidad se
	desplegará, ya sea una consulta de clima, consulta de hora, 
	de día de la semana, crear un recordatorio, evento, o hacer una
	pregunta de consulta a ChatGPT."""
	
	capacity = dict_with_data['capacidad']
	error = ""
	response = ""
	
	if capacity:
		text = dict_with_data['pregunta_original']
		dict_with_data['selector'] = 'otro'
		response,error = fetch_ai_response(client, text)
		
		if error == "":
			response = response.choices[0].message.content
		else:
			response = "Lo siento, hubo un error en la solicitud"\
						"Por favor, intenta de nuevo."
	else:
		try:
			selector = dict_with_data['selector']
		except:
			selector_tuple = calculate_action(dict_with_data)
			selector = selector_tuple[1]
			dict_with_data['selector'] = selector
			print("selector: ", selector_tuple)
		
		#try:
		if selector == 'agenda':
			response = agenda_api(dict_with_data)
		elif selector == 'reminders':
			response = reminders_api(dict_with_data)
		elif selector == 'date':
			response = date_api(dict_with_data['palabras_clave'])
		elif selector == 'time':
			response = time_api(dict_with_data['palabras_clave'])
		elif selector == 'weather':
			response = weather_api(dict_with_data['palabras_clave'])
		#except Exception as error:
		#	print("Hubo un error: ", error)

	return response

def setting_reminder(text):
	with open('data_response.json', 'r') as file_out:
		dict_resp = json.load(file_out)
		
	prompt = """ "{text}"\n Del texto anterior extrae las siguientes características, 
		las cuales deberán estar organizadas en un objeto json con estos campos: 
		event_date, event_time, event_description, event_duration. Cada campo lo
		clasificaras como sigue: 1. event_date, es la fecha en la que sucederá el
		evento, a su vez, puedes acomodar dentro otro objeto json con los campos: 
		date (fecha especifica en formado día-mes), weekday (puede ser lunes, martes, 
		miércoles, etc.), week (valor númerico), rellenándolos con la información extraida sobre la
		fecha. Si el día, weekday, no está especificado, por default elije el día 
		siguiente, o 'mañana' como default. Para los valores 'week' quiero una 
		representación por número enteros, 0 si no se especifica si es la siguiente semana, 
		1 si es la siguiente semana y así sucesivamente, si no se especifíca coloca None. 
		2. event_time, es la hora en formato de 24 horas. 3. event_description, 
		es la información del por qué se necesita la alarma/recordatorio, debe 
		iniciar con un verbo en infinitivo. 4. event_duration, por default considera 
		1 hora de duración, pero pueden ser incluso días. No necesito una explicación, 
		sólo el objeto json. Los valores de los campos deberán estar en español. Gracias :)""".format(text=text)
	
	response,error = fetch_ai_response(client, prompt)
	
	if error == "":
		response_text = response.choices[0].message.content
		
		indexes_json = []
		for i in range(len(response_text)):
			char_data = response_text[i]
			
			if (char_data == '{') | (char_data == '}'):
				indexes_json.append(i)
				
		index_curly_open = min(indexes_json)
		index_curly_close = max(indexes_json)
		
		pre_json = response_text[index_curly_open:index_curly_close + 1].replace("\n","")
		pre_json = pre_json.lower()

		dict_reminder = dict(json.loads(pre_json))
		dict_resp['datos_recordatorio'] = dict_reminder
		
		print("\n", dict_resp)
		resp_agenda = agenda_api(dict_resp)
		"""
		En esta sección se mandarán a llamar las funciones 'creating_text_response'
		y 'creating_voice_response' para no tener que llamar a la función 'analyze_text'
		(que internamente llama a las funciones mencionadas).
		
		Se buscará cambiar la llave 'respuesta_api' para la funcionalidad de agenda y alarma
		ya que sólo se tiene un texto de respuesta que será procesado para voz, y, después,
		se obtendrá la respuesta de la api.
		
		De esta forma se creará la respuesta en texto que sólo tomará en cuenta:
		la fecha, día y hora de inicio, y el título del recordatorio.
		
		Para la respuesta en texto para cuando se soliciten todos recordatorios
		pendientes, sólo se hará enfásis en el día y el recordatorio.
		"""
		dict_resp['respuesta_api'] = resp_agenda
		print(type(resp_agenda))
		
		for key in resp_agenda.keys():
			print(key + ": " + str(resp_agenda[key]))
			
		response_text = creating_text_response(dict_resp)
		print("setting_reminder(): response_text:", response_text)
		creating_voice_response(response_text)
		
	else:
		print("response:", response)

	return False

client = setup_openai_client(api_key)
