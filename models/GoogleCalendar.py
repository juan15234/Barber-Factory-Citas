from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import jsonify
from datetime import datetime, timedelta
import uuid
import os
import json
import base64

class GoogleCalendar:

    @classmethod
    def crear_evento(cls, nombre, servicio, barbero, correo_cliente, telefono_cliente, hora, fecha, duracion, nota_cliente):
        
        try:
            
            barbero = barbero.lower()
            
            if barbero == 'william':
                colorId = '3'
            
            elif barbero == 'ruben':
                colorId = '4'
                
            elif barbero == 'bryan':
                colorId = '6'
                
            elif barbero == 'marcos':
                colorId = '1'
                
            elif barbero == 'jhon':
                colorId = '2'
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            CALENDAR_ID = os.getenv('CORREO_BARBERIA')

            credentials = service_account.Credentials.from_service_account_file(
                'credenciales.json',
                scopes=SCOPES
            )
            
            inicio_str = f'{fecha}T{hora}:00'
            fecha_ini = datetime.strptime(inicio_str, '%Y-%m-%dT%H:%M:%S')

            fecha_fin = fecha_ini + timedelta(minutes=duracion)

            service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
            

            evento = {
                'summary':f'Nombre: {nombre} | Servicio: {servicio}',
                'description': f' Barbero: {barbero} | Correo: {correo_cliente} | Telefono:  {telefono_cliente} | Nota: {nota_cliente}',
                'start': {
                    'dateTime': fecha_ini.isoformat(),
                    'timeZone': 'America/Bogota',
                },
                'end':{
                    'dateTime': fecha_fin.isoformat(),
                    'timeZone': 'America/Bogota',
                },
                'colorId': colorId
            }

            evento = service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()
            evento_id = evento['id']
            return 'Cita Creada', evento_id
        except Exception as e:
            print(e)
            
    @classmethod
    def citas_en_calendario(cls, fecha_inicio, fecha_fin, barbero):

        from models.CitaModel import CitaModel
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        CALENDAR_ID = os.getenv('CORREO_BARBERIA')

        credentials = service_account.Credentials.from_service_account_file(
            'credenciales.json',
            scopes=SCOPES
        )

        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        
        time_min = fecha_inicio.isoformat() + 'Z'
        time_max = fecha_fin.isoformat() + 'Z'
        
        events_results = service.events().list(calendarId=CALENDAR_ID, timeMin=time_min,timeMax=time_max,singleEvents=True, orderBy='startTime').execute()
        events = events_results.get('items', [])

        citas = []
        
        for event in events:
            try:

                event_summary = event.get('summary', '')
                event_description = event.get('description', '')

                barbero_cita = extraer_campo('Barbero', event_description)

                if barbero_cita == barbero: 

                    fecha_hora = datetime.fromisoformat(event['start']['dateTime'])

                    usuario = extraer_campo('Nombre', event_summary)

                    email = extraer_campo('Correo', event_description)
                    telefono = extraer_campo('Telefono', event_description)
                    nota_cliente = extraer_campo('Nota', event_description)
                    servicio = extraer_campo('Servicio', event_summary)

                    duracion = CitaModel.duracion_servicio(servicio)

                    citas.append({'usuario':usuario,'barbero':barbero_cita, 'email':email,'telefono':telefono,'nota_cliente':nota_cliente, 'servicio':servicio,'duracion':duracion,'fecha_hora':fecha_hora})
            
            except Exception as e:
                print(e)
        return citas
            
            
    @classmethod
    def editar_evento(cls, cita_id, nuevo_barbero, nueva_hora, nueva_fecha):
        from models.CitaModel import CitaModel
        from models.Correo import Correo
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        CALENDAR_ID = os.getenv('CORREO_BARBERIA')

        credentials = service_account.Credentials.from_service_account_file(
            'credenciales.json',
            scopes=SCOPES
        )
        
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)

        now = datetime.utcnow().isoformat() + 'Z'
        
        events_results = service.events().list(calendarId=CALENDAR_ID, timeMin=now, singleEvents=True, orderBy='startTime').execute()

        events = events_results.get('items', [])

        for event in events:
            
            event_summary = event.get('summary', '')
            event_description = event.get('description', '')
            
            if event['id'] == cita_id:
                
                usuario = extraer_campo('Nombre', event_summary)
                servicio = extraer_campo('Servicio', event_summary)
                correo_cliente = extraer_campo('Correo', event_description)
                telefono_cliente = extraer_campo('Telefono', event_description)
                nota_cliente = extraer_campo('Nota', event_description)
                
                duracion = CitaModel.duracion_servicio(servicio)
                
                fecha_str = f'{nueva_fecha}T{nueva_hora}:00'
                
                nueva_fecha_ini = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%S')
                nueva_fecha_fin = nueva_fecha_ini + timedelta(minutes=duracion)
                
                colorId = event['colorId']
                
                evento_editado = {
                        'summary':f'Nombre: {usuario} | Servicio: {servicio}',
                        'description': f'Barbero: {nuevo_barbero} | Correo: {correo_cliente} | Telefono:  {telefono_cliente} | Nota: {nota_cliente}',
                        'start': {
                            'dateTime': nueva_fecha_ini.isoformat(),
                            'timeZone': 'America/Bogota',
                        },
                        'end':{
                            'dateTime': nueva_fecha_fin.isoformat(),
                            'timeZone': 'America/Bogota',
                        },
                        'colorId': colorId
                    }
                
                evento_editado = service.events().patch(calendarId=CALENDAR_ID, eventId=cita_id, body=evento_editado).execute()
                Correo.enviar_correo_cita_editada(correo_cliente,usuario,nuevo_barbero,nueva_hora,nueva_fecha,servicio,cita_id)
                return 'evento editado exitosamente'
            else:
                print('evento no encontrado')
            
    @classmethod
    def eliminar_evento(cls, cita_id):
        from models.Correo import Correo
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        CALENDAR_ID = os.getenv('CORREO_BARBERIA')

        credentials = service_account.Credentials.from_service_account_file(
            'credenciales.json',
            scopes=SCOPES
        )
        
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)

        now = datetime.utcnow().isoformat() + 'Z'
        

        events_results = service.events().list(calendarId=CALENDAR_ID, timeMin=now, singleEvents=True, orderBy='startTime').execute()

        events = events_results.get('items', [])

        for event in events:
            
            if event['id'] == cita_id:

                event_summary = event.get('summary', '')
                event_description = event.get('description', '')
        
                evento_eliminado = service.events().delete(calendarId=CALENDAR_ID, eventId=cita_id).execute()
                Correo.enviar_correo_cita_cancelada(extraer_campo('Correo',event_description),extraer_campo('Nombre',event_summary)) 
                return 'evento eliminado exitosamente'
    
    
def extraer_campo(campo, texto):
            if campo in texto:
                partes = texto.split(campo + ':')
                return partes[1].split('|')[0].strip()
            return 'Desconocido'