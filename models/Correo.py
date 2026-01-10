import yagmail
import os
from datetime import datetime
import threading

from models.GoogleCalendar import GoogleCalendar

class Correo:
    
    @classmethod
    def enviar_correo_confimacion_cita(cls, correo_cliente, nombre, barbero, hora, fecha, servicio, cita_id):
        try:
            
            
            link = f'http://127.0.0.1:5000/editar_cita/{cita_id}'
            
            mensaje_html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>

                    <style>
                        body{{
                            margin:0;
                            padding:30px;
                        }}

                        .carta{{
                            background-color: lightblue;
                            color: white;
                        }}

                        .carta a{{
                            color: white;
                            background-color: black;
                            border-radius: 20px;
                            padding: 5px;
                        }}
                    </style>

                </head>
                <body>
                    <h1>The Barber Factory</h1>
                    <div class="carta">
                        <h4>¡Hola {nombre}!</h4>
                        <h4>Acabas de agendar una cita con <strong>{barbero}</strong></h4>
                        <h4>Fecha: <strong>{fecha}</strong></h4>
                        <h4>Hora: <strong>{hora}</strong></h4>
                        <h4>Servicio: <strong>{servicio}</strong></h4>
                        <h4>¿Quieres editar o eliminar la cita?, <a href="{link}">¡Preciona aqui!</a></h4>
                    </div>
                </body>
                </html>
            """
            
            correo_barberia = os.getenv('CORREO_BARBERIA')
            contraseña_app = os.getenv('CONTRASENA_APP')
            
            yag = yagmail.SMTP(correo_barberia, contraseña_app)
        
            yag.send(
                to=f'{correo_cliente}',
                subject='Cita The Barber Factory',
                contents=[mensaje_html]
            )
        except Exception as e:
            print(e)

    @classmethod
    def enviar_correo_cita_editada(cls, correo_cliente, nombre, barbero, hora, fecha, servicio, cita_id):
        try:
            
            
            link = f'http://127.0.0.1:5000/editar_cita/{cita_id}'
            
            mensaje_html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>

                    <style>
                        .carta{{
                            background-color: rgb(63, 65, 71);
                            color: white;
                        }}

                        .carta a{{
                            color: white;
                            background-color: black;
                            border-radius: 20px;
                            padding: 5px;
                        }}
                    </style>

                </head>
                <body>
                    <h1>The Barber Factory</h1>
                    <div class="carta">
                        <h4>¡Hola {nombre}! Tu cita a sido editada</h4>
                        <h4>Barbero: <strong>{barbero}</strong></h4>
                        <h4>Fecha: <strong>{fecha}</strong></h4>
                        <h4>Hora: <strong>{hora}</strong></h4>
                        <h4>Servicio: <strong>{servicio}</strong></h4>
                        <h4>¿Quieres editar o eliminar la cita?, <a href="{link}">¡Preciona aqui!</a></h4>
                    </div>
                </body>
                </html>
            """
            
            correo_barberia = os.getenv('CORREO_BARBERIA')
            contraseña_app = os.getenv('CONTRASENA_APP')
            
            yag = yagmail.SMTP(correo_barberia, contraseña_app)
        
            yag.send(
                to=f'{correo_cliente}',
                subject='Cita The Barber Factory',
                contents=[mensaje_html]
            )
        except Exception as e:
            print(e)

    @classmethod
    def enviar_correo_cita_cancelada(cls, correo_cliente, nombre):
        try:
            
            
            link = 'http://127.0.0.1:5000/'
            
            mensaje_html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>

                    <style>
                        .carta{{
                            background-color: rgb(63, 65, 71);
                            color: white;
                        }}

                        .carta a{{
                            color: white;
                            background-color: black;
                            border-radius: 20px;
                            padding: 5px;
                        }}
                    </style>

                </head>
                <body>
                    <h1>The Barber Factory</h1>
                    <div class="carta">
                        <h4>¡Hola {nombre}! Tu cita a sido cancelada</h4>
                        <h4>¿Quieres programar otra cita?, <a href="{link}">¡Preciona aqui!</a></h4>
                    </div>
                </body>
                </html>
            """
            
            correo_barberia = os.getenv('CORREO_BARBERIA')
            contraseña_app = os.getenv('CONTRASENA_APP')
            
            yag = yagmail.SMTP(correo_barberia, contraseña_app)
        
            yag.send(
                to=f'{correo_cliente}',
                subject='Cita The Barber Factory',
                contents=[mensaje_html]
            )
        except Exception as e:
            print(e)
        
    @classmethod
    def enviar_recordatorio(cls):
        
        fecha_inicio = datetime.now
        fecha_fin = fecha_inicio.replace(hour=23, minute=59, second=59)
        citas = []

        citas = GoogleCalendar.citas_en_calendario(fecha_inicio,fecha_fin)
        
        for cita in citas:
            
            nombre = cita[1]
            fecha_hora = cita[3]
            barbero_numero = int(cita[2])
            correo_cliente = cita[4]
            servicio_numero = int(cita[6])
            
            hora = fecha_hora.time()
            
            
            servicio_texto = Correo.servicio_numero_to_servicio_texto(servicio_numero)
                
            barbero = Correo.barbero_numero_to_barbero_texto(barbero_numero)

            try:

                mensaje_html = f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Document</title>

                        <style>
                            .carta{{
                                background-color: rgb(63, 65, 71);
                                color: white;
                            }}

                            .carta a{{
                                color: white;
                                background-color: black;
                                border-radius: 20px;
                                padding: 5px;
                            }}
                        </style>

                    </head>
                    <body>
                        <h2>The Barber Factory</h2>
                        <div class="carta">
                            <p>¡Hola {nombre}!</p>
                            <p>Recuerda que tienes una cita el dia de hoy con <strong>{barbero}</strong></p>
                            <p>Hora: <strong>{hora}</strong></p>
                            <p>Servicio: <strong>{servicio_texto}</strong></p>
                        </div>
                    </body>
                    </html>
                """

                correo_barberia = os.getenv('CORREO_BARBERIA')
                contraseña_app = os.getenv('CONTRASENA_APP')

                yag = yagmail.SMTP(correo_barberia, contraseña_app)

                yag.send(
                    to=f'{correo_cliente}',
                    subject='Recordatorio Cita The Barber Factory',
                    contents=[mensaje_html]
                )
                
            except Exception as e:
                print(e)
        
        return 'se ha enviado los recordatorios a los correos de los clientes'
    
def enviar_correo_async(*args):
    Correo.enviar_correo_confimacion_cita(*args)
    print('correo enviado')
