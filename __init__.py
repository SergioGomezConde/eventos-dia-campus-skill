from mycroft import MycroftSkill, intent_file_handler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
from datetime import date

# Fichero JSON donde almacenar la informacion
ficheroJSON = "/home/serggom/data.json"
informacion = {'asignaturas': [], 'usuario': [], 'eventos': [], 'mensajes': []}


def inicio_sesion(self):
    # Datos de acceso fijos
    usuario = 'e71180769r'
    contrasena = 'p5irZ9Jm4@9C#6WUaE!z9%@V'

    # Modo headless
    options = Options()
    options.headless = True
    options.add_argument("--windows-size=1920,1200")

    self.speak("Buscando la informacion...")

    # Acceso a pagina
    driver = webdriver.Chrome(options=options)
    driver.get('https://campusvirtual.uva.es/login/index.php')

    # Inicio de sesion
    driver.find_element(by=By.NAME, value='adAS_username').send_keys(usuario)
    driver.find_element(
        by=By.NAME, value='adAS_password').send_keys(contrasena)
    driver.find_element(by=By.NAME, value='adAS_submit').click()

    # Aceptar cookies
    driver.implicitly_wait(10)
    driver.find_element(
        by=By.XPATH, value='/html/body/div[1]/div/a[1]').click()

    return driver


def mesANumero(x):  # Funcion que devuelve el numero de mes introducido de manera escrita
    return{
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


# Funcion para dar formato a una fecha y devolverla en la respuesta
def formatear_fecha(fecha_a_formatear):
    fecha_separada = fecha_a_formatear.split(", ")
    if(fecha_separada[0] == "Mañana" or fecha_separada[0] == "Hoy"):
        hora = fecha_separada[1]
    else:
        hora = fecha_separada[2]
    fecha_formateada = "A las " + hora
    return fecha_formateada


# Funcion que devuelve una lista con dia, mes y anio
def formatear_fecha_introducida(dia_a_formatear):
    dia_en_numero = str(dia_a_formatear).split(" ")[1]
    mes_en_numero = mesANumero(str(dia_a_formatear).split(" ")[3])

    dia_separado = [dia_en_numero, mes_en_numero, str(date.today().year)]

    return dia_separado


class EventosDiaCampus(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('campus.dia.eventos.intent')
    def handle_campus_dia_eventos(self, message):

        # Solicitud y obtencion del dia del que buscar los eventos
        dia_response = self.get_response('solicitardia')
        self.log.info(dia_response)

        # Por defecto se toma el anio actual
        fecha = str(dia_response).split("el ")[1] + " de " + str(date.today().year)

        # Obtencion de los numeros de dia, mes y anio
        dia_separado = formatear_fecha_introducida(dia_response)
        numero_dia = int(dia_separado[0])
        numero_mes = int(dia_separado[1])
        numero_anio = int(dia_separado[2])

        # Obtencion de la fecha en segundos desde epoch
        segundos = (datetime(numero_anio, numero_mes, numero_dia,
                    0, 0) - datetime(1970, 1, 1)).total_seconds()

        # Comprobacion de que la fecha introducida aun no ha pasado
        if (numero_mes < date.today().month) or ((numero_mes == date.today().month) and (numero_dia < date.today().day)):
            self.speak("El " + fecha + " ya ha pasado")

        # Comprobacion de si la fecha introducida es el dia actual
        elif ((numero_dia == date.today().day) and (numero_mes == date.today().month) and (numero_anio == date.today().year)):
            driver = inicio_sesion(self)

            # Acceso al dia del que buscar los eventos
            driver.get(
                'https://campusvirtual.uva.es/calendar/view.php?view=day&time=' + str(segundos))

            # Obtencion de la lista de eventos del dia
            eventos_dia = driver.find_elements(by=By.CLASS_NAME, value='event')
            
            
            for evento in eventos_dia:
                informacion['eventos'].append({
                    'nombre': evento.find_element(by=By.TAG_NAME, value='h3').text,
                    'fecha': formatear_fecha(evento.find_element(by=By.CLASS_NAME, value='col-11').text.split(
                    " » ")[0])
                })

            with open(ficheroJSON, 'w') as ficheroDatos:
                json.dump(informacion, ficheroDatos, indent=4)

            # Obtencion del numero de eventos del dia
            numero_eventos = len(eventos_dia)

            # Respuesta con los eventos del dia
            if numero_eventos == 0:
                self.speak("Hoy no tienes ningun evento")

            elif numero_eventos == 1:
                self.speak_dialog('Hoy tienes un evento')
                evento_dia = eventos_dia[0]
                self.speak(formatear_fecha(evento_dia.find_element(by=By.CLASS_NAME, value='col-11').text.split(
                    " » ")[0]) + " tienes " + evento_dia.find_element(by=By.TAG_NAME, value='h3').text)
            else:
                self.speak_dialog('campus.dia.hoy.eventos', data={
                                  'numero_eventos': numero_eventos})
                for evento_dia in eventos_dia:
                    self.speak(formatear_fecha(evento_dia.find_element(by=By.CLASS_NAME, value='col-11').text.split(
                        " » ")[0]) + " tienes " + evento_dia.find_element(by=By.TAG_NAME, value='h3').text)

        else:
            driver = inicio_sesion(self)

            # Acceso al dia del que buscar los eventos
            driver.get(
                'https://campusvirtual.uva.es/calendar/view.php?view=day&time=' + str(segundos))

            # Obtencion de la lista de eventos del dia
            eventos_dia = driver.find_elements(by=By.CLASS_NAME, value='event')

            # Obtencion del numero de eventos del dia
            numero_eventos = len(eventos_dia)

            # Respuesta con los eventos del dia
            if numero_eventos == 0:
                self.speak("El " + fecha + " no tienes ningun evento")

            elif numero_eventos == 1:
                self.speak_dialog('campus.dia.unevento', data={'dia': fecha})
                evento_dia = eventos_dia[0]
                self.speak(formatear_fecha(evento_dia.find_element(by=By.CLASS_NAME, value='col-11').text.split(
                    " » ")[0]) + " tienes " + evento_dia.find_element(by=By.TAG_NAME, value='h3').text)
            else:
                self.speak_dialog('campus.dia.eventos', data={
                                  'dia': fecha, 'numero_eventos': numero_eventos})
                for evento_dia in eventos_dia:
                    self.speak(formatear_fecha(evento_dia.find_element(by=By.CLASS_NAME, value='col-11').text.split(
                        " » ")[0]) + " tienes " + evento_dia.find_element(by=By.TAG_NAME, value='h3').text)


def create_skill():
    return EventosDiaCampus()

