from flask import Flask, render_template, request, jsonify, session, url_for
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from config import config
from models.CitaModel import CitaModel
from models.Correo import Correo
from models.GoogleCalendar import GoogleCalendar

load_dotenv(dotenv_path=".env")

app = Flask(__name__)
app.config.from_object(config['development'])
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/horas-disponibles')
def horas_disponibles():
    fecha = request.args.get("fecha")
    barbero = request.args.get("barbero")
    
    horas_disponibles = CitaModel.horas_disponibles( fecha, barbero)
    
    return jsonify(horas_disponibles)

@app.route('/crear_cita')
def crear_cita():
    try:
        
        nombre = request.args.get('nombre')
        correo_cliente = request.args.get('correo_cliente')
        telefono_cliente = request.args.get('telefono_cliente')
        barbero = request.args.get('barbero')
        fecha = request.args.get('fecha')
        hora = request.args.get('hora')
        servicio = session.get('servicio')
        duracion = session.get('duracion')
        nota_cliente = request.args.get('nota')

        if not nota_cliente:
            nota_cliente = 'nada'

        session['nombre'] = nombre
        session['barbero'] = barbero
        session['hora'] = hora
        session['fecha'] = fecha
        session['correo_cliente'] = correo_cliente
        session['telefono_cliente'] = telefono_cliente
        session['nota_cliente'] = nota_cliente

        cita_creada, enviar_correo,cita_id = CitaModel.crear_cita(nombre, barbero, fecha, hora, correo_cliente, telefono_cliente, servicio, duracion , nota_cliente)
        session['cita_id'] = cita_id

        if cita_creada == 'Cita Creada':
            return jsonify({'ok': True, 'estatus': 'Cita creada', 'estatus_correo':enviar_correo})
        else:
            return jsonify({'ok':False, 'estatus': 'Cita no creada'})
        
    except Exception as e:
        print(e)


@app.route('/agendar/<servicio>')
def agendar(servicio):
    
    duracion = CitaModel.duracion_servicio(servicio)
    session['servicio'] = servicio
    session['duracion'] = duracion
    return render_template("agendar.html")

@app.route('/editar_cita/<cita_id>', methods=['GET'])
def editar_cita(cita_id):
    
    session['cita_id'] = cita_id
    
    
    return render_template('editar_cita.html')

@app.route('/editar_cita_backend', methods=['GET', 'POST'])
def editar_cita_backend():
    nueva_fecha = request.args.get('nueva_fecha')
    nueva_hora = request.args.get('nueva_hora')
    nuevo_barbero = request.args.get('nuevo_barbero')
    cita_id = session.get('cita_id')

    
    cita_editada,cita_id = CitaModel.editar_cita(nueva_fecha, nueva_hora, nuevo_barbero, cita_id)
    
    if cita_editada == 'evento editado exitosamente':
            
        return jsonify({'ok': True, 'estatus_google_calendar':cita_editada, 'cita_id': cita_id})
    else:
        return jsonify({'ok':False, 'estatus_google_calendar':'hubo un error al editar la cita'})

@app.route('/cancelar_cita_backend')
def cancelar_cita_backend():
    cita_id = session.get('cita_id')
    
    cita_cancelada = GoogleCalendar.eliminar_evento(cita_id)
    
    print(cita_cancelada)
    
    session.clear()
    
    if cita_cancelada == 'evento eliminado exitosamente':
        return jsonify({'ok': True, 'estatus_google_calendar':cita_cancelada,'cita_id': cita_id})
    else:
        return jsonify({'ok':False, 'estatus_google_calendar':cita_cancelada})

@app.route('/')
def main():
    return render_template('home.html')


#ENVIO DE CORREOS DE RECORDATORIO DE MANERA AUTOMATICA
scheduler = BackgroundScheduler()
scheduler.add_job(Correo.enviar_recordatorio, trigger='cron', hour=8, misfire_grace_time=3600)
scheduler.start()

if __name__ == '__main__':
    app.run()
