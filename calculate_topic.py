TIME_COMPARISON = {
	"sentence": ["qué hora es", "puedes decirme qué hora es"],
	"list": ["tiempo", "actual", "consulta", "hora", "horario", "información", "momento", "ahora", "solicitud", "reloj", "consultar"],
	"topic": "time"
		}

DAY_COMPARISON = {
	"sentence": ["qué día es hoy","qué día será mañana"],
	"list": ["fecha", "día", "actual", "consulta", "calendario", "consultar", "mañana", "siguiente", "mañana"],
	"topic": "date"
		}

AGENDA_COMPARISON = {
	"sentence": ["programa un recordatorio", "crea una alarma", "agenda una cita", "agenda una reunión"],
	"list": ['agenda', 'agendar', 'reunión', 'programar', 'cita', 'evento', 'calendarizar', 'organizar', 'coordinar', 'recordatorio',  'temporizador', 'crear', 'alarma', 'organización', 'gestión'],
	"topic": "agenda"
		}
	
WEATHER_COMPARISON = {
	"sentence": ["cuál es el clima hoy", "cómo es el tiempo hoy", "cuál será el clima mañana"],
	"list": ['clima', 'hoy', 'temperatura', 'pronóstico', 'meteorológico', "tiempo", 'condiciones', 'meteorológicas', 'predicción'],
	"topic": "weather"
		}
	
REMINDERS_COMPARISON = {
	"sentence": ["qué pendientes tengo para hoy", "qué pendientes tengo para esta semana"],
	"list": ["pendientes", "tareas", "agenda", "planificación", "diaria", "recordatorios", "organización", "actividades", "eventos"],
	"topic": "reminders"
		}

COMPARISON = [TIME_COMPARISON, DAY_COMPARISON, AGENDA_COMPARISON, WEATHER_COMPARISON, REMINDERS_COMPARISON]

def calculate_action(dict_data):
	key_words = dict_data['palabras_clave']
	points = []

	
	for list_kw in COMPARISON:
		points_sum = 0
		for keyword in list_kw['list']:
			for keyword_dict in key_words:
				points_sum += 0.2 if keyword_dict == keyword else 0

		points.append((points_sum, list_kw['topic']))
	
	points.sort(reverse=True)
	return points[0]
	

#dict_data = {'palabras_clave': ['agenda', 'reunión', 'organizar', 'programar', 'citar'], 'capacidad': True, 'pregunta_original': 'agenda una reunión'}
#calculate_action(dict_data)
