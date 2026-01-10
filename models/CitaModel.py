from datetime import datetime, timedelta
import threading

from models.GoogleCalendar import GoogleCalendar
from models.Correo import enviar_correo_async


class CitaModel:
    
    @classmethod
    def horas_disponibles(cls, fecha, barbero):
        
        try:

            fecha_inicio = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_fin = fecha_inicio.replace(hour=23, minute=59, second=59)
            citas = []
            
            citas = GoogleCalendar.citas_en_calendario(fecha_inicio, fecha_fin, barbero)

            minutos_ocupados = []
            
            for cita in citas:
                duracion = cita['duracion']
                fecha_hora = cita['fecha_hora']

                hora = datetime.strftime(fecha_hora, "%H:%M")
                hora_inicio = datetime.strptime(hora, "%H:%M")
                
                for i in range(duracion):
                    bloque = (hora_inicio + timedelta(minutes=i)).strftime("%H:%M")
                    minutos_ocupados.append(bloque)
                    
                    
            inicio_mañana = datetime.strptime("10:00", "%H:%M")
            fin_mañana = datetime.strptime("11:59", "%H:%M")
            
            inicio_tarde = datetime.strptime("12:00","%H:%M")
            fin_tarde = datetime.strptime("17:59","%H:%M")
            
            inicio_noche = datetime.strptime("18:00","%H:%M")
            fin_noche = datetime.strptime("19:00","%H:%M")
                    
            minutos_ocupados = sorted(minutos_ocupados)
            bloques_ocupados = []
            bloque_actual = []

            def hora_a_minutos(hora):
                h, m = map(int, hora.split(":"))
                return h * 60 + m

            for i, hora in enumerate(minutos_ocupados):
                if datetime.strptime(hora, "%H:%M") > fin_noche:
                    break
                else:
                    if not bloque_actual:
                        bloque_actual.append(hora)
                    else:
                        hora_anterior = hora_a_minutos(bloque_actual[-1])
                        hora_actual = hora_a_minutos(hora)
                        if hora_actual == hora_anterior + 1:
                            bloque_actual.append(hora)
                        else:
                            bloques_ocupados.append(bloque_actual)
                            bloque_actual = [hora]

            if bloque_actual:
                bloques_ocupados.append(bloque_actual)
                
            
            horas_disponibles = []
            
            #BLOQUE HORARIO MAÑANA
            
            bloque_mañana = []

            while inicio_mañana <= fin_mañana:
                hora_str = inicio_mañana.strftime("%H:%M")
                if hora_str not in minutos_ocupados:
                    bloque_mañana.append(hora_str)
                inicio_mañana += timedelta(minutes=15)
                
            horas_disponibles.append(bloque_mañana)
                
            #BLOQUE HORARIO TARDE
            
            bloque_tarde = []
                
            while inicio_tarde <= fin_tarde:
                hora_str = inicio_tarde.strftime("%H:%M")
                if hora_str not in minutos_ocupados:
                    bloque_tarde.append(hora_str)
                inicio_tarde += timedelta(minutes=15)
            
            horas_disponibles.append(bloque_tarde)
            
            #BLOQUE HORARIO NOCHE
            
            bloque_noche = []
                
            while inicio_noche <= fin_noche:
                hora_str = inicio_noche.strftime("%H:%M")
                if hora_str not in minutos_ocupados:
                    bloque_noche.append(hora_str)
                inicio_noche += timedelta(minutes=15)
            
            horas_disponibles.append(bloque_noche)
                
            
            if horas_disponibles == []:
                return "no citas disponibles"
            else:
                return horas_disponibles, bloques_ocupados
        
        except Exception as e:
            print(e)
            
            
    @classmethod
    def crear_cita(cls, usuario, barbero, fecha, hora, correo_cliente, telefono_cliente, servicio, duracion,nota_cliente):
        try:

            cita_creada,cita_id = GoogleCalendar.crear_evento(usuario,servicio,barbero,correo_cliente,telefono_cliente,hora,fecha,duracion,nota_cliente)

            threading.Thread(
                target=enviar_correo_async,
                args=(correo_cliente, usuario, barbero, hora, fecha, servicio, cita_id),
                daemon=True
            ).start()

            return cita_creada,True,cita_id
            
        except Exception as e:
            print(e)
            return e
            
    @classmethod
    def editar_cita(cls, nueva_fecha, nueva_hora, nuevo_barbero, cita_id):
        try:
            
            fecha_hora_obj = f'{nueva_fecha} {nueva_hora}'
            
            fecha_obj = datetime.strptime(fecha_hora_obj, '%Y-%m-%d %H:%M')

            if fecha_obj >= datetime.now():
                cita_editada = GoogleCalendar.editar_evento(cita_id,nuevo_barbero,nueva_hora,nueva_fecha)

                return cita_editada,cita_id
            else:
                return 'Hora o fecha no disponible'
            
        except Exception as e:
            print(e)
    
    @classmethod
    def duracion_servicio(cls, servicio):
        if servicio == 'corte':
            duracion = 45
            return duracion
        
        elif servicio == 'afeitado_barba':
            duracion =30
            return duracion
        
        elif servicio == 'corte_barba':
            duracion = 60
            return duracion
        
        elif servicio == 'arreglo_barba':
            duracion = 30
            return duracion
        
        elif servicio == 'barba_tinte':
            duracion = 30
            return duracion
        
        elif servicio == 'limpieza_facial':
            duracion = 30
            return duracion
        
        elif servicio == 'corte_alizado':
            duracion = 45
            return duracion
        
        elif servicio == 'depilacion_cpn':
            duracion = 30
            return duracion
                