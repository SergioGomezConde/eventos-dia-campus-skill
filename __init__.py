from mycroft import MycroftSkill, intent_file_handler


class EventosDiaCampus(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('campus.dia.eventos.intent')
    def handle_campus_dia_eventos(self, message):
        self.speak_dialog('campus.dia.eventos')


def create_skill():
    return EventosDiaCampus()

