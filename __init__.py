import json
import os
from datetime import datetime

from mycroft import MycroftSkill, intent_file_handler

# Fichero JSON donde almacenar la informacion
ficheroJSON = "/home/serggom/scraping/datos.json"


def mes_a_numero(x):  # Funcion que devuelve el numero de mes introducido de manera escrita
    return {
        'enero': "01",
        'febrero': "02",
        'marzo': "03",
        'abril': "04",
        'mayo': "05",
        'junio': "06",
        'julio': "07",
        'agosto': "08",
        'septiembre': "09",
        'octubre': "10",
        'noviembre': "11",
        'diciembre': "12",
    }[x]


# Funcion que devuelve una lista con dia, mes y anio
def formatear_fecha_introducida(dia_a_formatear):
    dia_en_numero = str(dia_a_formatear).split(" ")[0]
    mes_en_numero = mes_a_numero(str(dia_a_formatear).split(" ")[2])
    now = datetime.now()
    dia_separado = [dia_en_numero, mes_en_numero, str(now.year)]

    return dia_separado


class EventosDiaCampus(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('campus.dia.eventos.intent')
    def handle_campus_dia_eventos(self, message):

        intent = str(message.data.get('utterance'))

        if "dia" in intent:
            fecha_introducida = intent.split("dia ")[1]

        elif "día" in intent:
            fecha_introducida = intent.split("día ")[1]

        elif " del " in intent:
            fecha_introducida = intent.split("del ")[1]

        else:
            fecha_introducida = intent.split("el ")[1]

        self.speak(fecha_introducida)

        # Lectura de la informacion del fichero JSON
        if os.path.exists(ficheroJSON):
            now = datetime.now()

            # Por defecto se toma el anio actual
            fecha = intent + " de " + str(now.year)

            # Obtencion de los numeros de dia, mes y anio
            dia_separado = formatear_fecha_introducida(fecha_introducida)
            numero_dia = int(dia_separado[0])
            if numero_dia < 10:
                numero_dia_string = "0" + str(numero_dia)
            else:
                numero_dia_string = str(numero_dia)

            numero_mes = int(dia_separado[1])
            if numero_mes < 10:
                numero_mes_string = "0" + str(numero_mes)
            else:
                numero_mes_string = str(numero_mes)

            numero_anio = int(dia_separado[2])

            fecha_a_buscar = numero_dia_string + "/" + numero_mes_string + "/" + str(numero_anio)

            # Comprobacion de que la fecha introducida aun no ha pasado
            if (numero_mes < now.month) or (
                    (numero_mes == now.month) and (numero_dia < now.day)):
                self.speak("El " + fecha + " ya ha pasado")

            # Comprobacion de si la fecha introducida es el dia actual
            elif ((numero_dia == now.day) and (numero_mes == now.month) and (
                    numero_anio == now.year)):

                # Lectura de la informacion del fichero JSON
                with open(ficheroJSON) as ficheroEventos:
                    data = json.load(ficheroEventos)
                    i = 0

                    for event in data['eventos']:

                        if event['fecha'] == fecha_a_buscar:
                            i = i + 1

                    if i > 0:

                        for event in data['eventos']:

                            if event['fecha'] == fecha_a_buscar:
                                hora = int(event['hora'].split(":")[0])
                                minuto = int(event['hora'].split(":")[1])

                                if (hora > now.hour) or ((hora == now.hour) and (minuto > now.minute)):
                                    self.speak("Hoy a las " + event['hora'] + " tienes " + event['nombre'])

                    else:
                        self.speak("Hoy no tienes ningún evento")

            else:
                now = datetime.now()
                hora = now.hour
                # Lectura de la informacion del fichero JSON
                with open(ficheroJSON) as ficheroEventos:
                    data = json.load(ficheroEventos)
                    i = 0

                    for event in data['eventos']:
                        if event['fecha'] == fecha_a_buscar:
                            i = i + 1

                    if i > 0:
                        for event in data['eventos']:
                            if event['fecha'] == fecha_a_buscar:
                                self.speak("El " + fecha_introducida + " a las " + event['hora'] + " tienes " + event[
                                    'nombre'])

                    else:
                        self.speak("El " + fecha_introducida + " no tienes ningún evento")

        else:
            self.speak("Lo siento, no dispongo de esa información")


def create_skill():
    return EventosDiaCampus()
