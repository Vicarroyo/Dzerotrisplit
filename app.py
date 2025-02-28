from flask import Flask, render_template, request, redirect, url_for
from utils.running import (
    calculate_pace,
    estimate_running_times,
    validate_time_format,
    calculate_anaerobic_threshold,
    classify_anaerobic_threshold,
    process_running_data
)
from utils.swimming import estimate_swim_times, calculate_zones
from utils.cycling import calculate_ftp, classify_ftp, calculate_ftp_zones, calculate_corrected_speed, calculate_tri_speeds, hours_to_hms_str
from flask import Flask, render_template, request, session
from datetime import timedelta

# Importación de funciones desde utils.triatlon
from utils.triatlon import (
    estimate_swim_times,
    calculate_ftp,
    classify_ftp,
    calculate_event_watts,
    calculate_pace,
    calculate_anaerobic_threshold,
    convert_seconds_to_min_km,
    estimate_running_times,
    calculate_event_running_times,
    classify_anaerobic_threshold,
    # Funciones nuevas de ciclismo
    calculate_speed,
    calculate_corrected_speed,
    hours_to_hms_str,
    calculate_tri_speeds,
    calculate_adjusted_time,
    convert_seconds_to_hms
)

from utils.triatlon import convert_seconds_to_hms

app = Flask(__name__)
app.jinja_env.filters['convert_seconds_to_hms'] = convert_seconds_to_hms


# Crear la instancia de Flask
app = Flask(__name__)

from flask import Flask

app = Flask(__name__)
app.secret_key = "una_clave_secreta_muy_aleatoria_y_segura"  # Cambia este valor por uno único y secreto

# Ruta de inicio
@app.route('/')
def home():
    return render_template('home.html')




# Página para carrera
@app.route('/running', methods=['GET', 'POST'])
def running():
    if request.method == 'POST':
        try:
            # Recoger los datos del formulario
            distance = float(request.form['distance'])  # Distancia en km
            gender = request.form['gender']
            hours = int(request.form['hours'])
            minutes = int(request.form['minutes'])
            seconds = int(request.form['seconds'])

            # Convertir tiempo a formato hh:mm:ss
            time = f"{hours:02}:{minutes:02}:{seconds:02}"

            # Validar el formato del tiempo (según tu propia función)
            validate_time_format(time)

            # Procesar los datos de carrera (p.ej. con tu "process_running_data")
            results = process_running_data(distance, time, gender)

            # EJEMPLO: Si quieres guardar "estimated_times" en la sesión, hazlo aquí:
            session['estimated_times'] = results["estimated_times"]
            session['original_pace'] = results["pace"]  # si quieres guardar el pace
            session['selected_distance'] = distance      # si necesitas la distancia

            # Renderizar los resultados y pasar los cálculos al template
            return render_template(
                'running_results.html',
                selected_distance=distance,  # Pasar la distancia seleccionada
                pace=results["pace"],
                anaerobic_threshold=results["anaerobic_threshold"],
                ua_category=results["ua_category"],
                estimated_times=results["estimated_times"],
                zones=results["zones"],  # Zonas calculadas
            )
        except ValueError as e:
            return f"Error: {e}"  # Enviar mensaje de error si ocurre alguna excepción

    return render_template('running_input.html')


@app.route('/ajustes_running', methods=['GET', 'POST'])
def ajustes_running():
    # 1) Recuperamos la info de la sesión
    estimated_times = session.get('estimated_times', {})
    original_pace = session.get('original_pace', "00:00:00")
    selected_distance = session.get('selected_distance', None)

    # 2) Opcional: Manejar POST si necesitas
    if request.method == 'POST':
        # Ejemplo: capturar algún dato enviado desde la plantilla
        # new_pace = request.form.get('new_pace')
        # ... procesar ...
        pass

    # 3) Renderizamos 'ajustes_running.html', pasando estimated_times y otros datos
    return render_template(
        'ajustes_running.html',
        results_dict=estimated_times,  # O el nombre que prefieras
        original_pace=original_pace,
        selected_distance=selected_distance,
        estimated_times=estimated_times
    )




@app.route('/swimming', methods=['GET', 'POST'])
def swimming():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            distance = float(request.form['distance'])
            hours = int(request.form['hours'])
            minutes = int(request.form['minutes'])
            seconds = int(request.form['seconds'])
            
            # Convertir el tiempo total a segundos
            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            
            # Calcular el ritmo promedio en segundos por 100m
            pace_seconds_per_100m = (total_seconds / distance) * 100
            
            # Convertir el ritmo a formato MM:SS
            pace_minutes = int(pace_seconds_per_100m // 60)
            pace_remainder_seconds = int(pace_seconds_per_100m % 60)
            pace = f"{pace_minutes:02}:{pace_remainder_seconds:02}"
            
            # Formatear el tiempo total en hh:mm:ss
            total_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Calcular estimaciones, CSS y categoría usando la función correspondiente
            estimates, css, css_category = estimate_swim_times(distance, total_time)
            
            # Calcular zonas de entrenamiento
            css_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], css.split(":")))
            zones = calculate_zones(css_seconds)
            
            # Renderizar la plantilla de resultados
            return render_template(
                'swimming_results.html',
                selected_distance=distance,
                total_time=total_time,
                pace=pace,
                estimates=estimates,
                css=css,
                css_category=css_category,
                zones=zones,
            )
        except Exception as e:
            return f"Error inesperado: {e}"
    
    # Si es GET, se muestra el formulario
    return render_template('swimming_input.html')

@app.route('/ajustes_swim', methods=['GET'])
def ajustes_swim():
    # Extraer los parámetros de la URL
    distance = request.args.get('distance', type=float)
    pace = request.args.get('pace', type=str)
    css = request.args.get('css', type=str)
    category = request.args.get('category', type=str)
    
    # Si faltan parámetros, redirige al test
    if distance is None or pace is None or css is None or category is None:
        return redirect(url_for('swimming'))
    
    # Renderiza la plantilla de ajustes pasando los valores iniciales
    return render_template('ajustes_swim.html', distance=distance, pace=pace, css=css, category=category)




from flask import render_template, request

# Diccionario para mapear valor CdA a etiqueta
CDA_MAP = {
    0.2:   "posición élite",
    0.225: "posición avanzada",
    0.25:  "posición estándar",
    0.275: "posición poco aerodinámica",
    0.3:   "sin posición aerodinámica"
}

def get_time_loss_percentage(desnivel):
    """
    Devuelve el porcentaje de pérdida de tiempo basado en el desnivel acumulado.
    """
    if desnivel <= 500:
        return 0.031  # 3.1%
    elif desnivel <= 1000:
        return 0.064  # 6.4%
    elif desnivel <= 1500:
        return 0.099  # 9.9%
    elif desnivel <= 2000:
        return 0.137  # 13.7%
    elif desnivel <= 2500:
        return 0.177  # 17.7%
    elif desnivel <= 3000:
        return 0.22   # 22%
    else:
        return 0.22   # Máximo 22%

@app.route('/cycling', methods=['GET', 'POST'])
def cycling():
    if request.method == 'POST':
        # 1) Recogemos datos del formulario
        gender = request.form.get('gender', 'male')  # Valor por defecto 'male' si no se proporciona
        weight = float(request.form.get('weight', 70))  # Peso en kg
        bike_weight = float(request.form.get('bike_weight', 10))  # Peso de la bicicleta en kg
        power = float(request.form.get('power', 300))  # Potencia en W
        test_time = int(request.form.get('test_time', 20))  # Tiempo del test en minutos
        cda_value = float(request.form.get('cda', 0.25))  # CdA

        try:
            # 2) Cálculos
            ftp, ftp_kg = calculate_ftp(gender, weight, power, test_time)  # Función personalizada
            category = classify_ftp(ftp_kg, gender)  # Función personalizada
            zones = calculate_ftp_zones(ftp)  # Función personalizada

            # Calcular masa total
            mass_total = weight + bike_weight  # Masa total en kg

            # Calcular velocidad al 100% FTP utilizando la fórmula precisa
            power_objetivo = ftp * 1.0  # Intensidad al 100%
            velocidad_kmh_100 = calculate_corrected_speed(
                ftp=ftp,
                mass_total=mass_total,  # Pasamos mass_total aquí
                cda=cda_value,
                intensity=1.0,  # 100%
                rho=1.225,
                alpha=0.95
            )
            velocidad_kmh_100 = round(velocidad_kmh_100, 2)

            # Calcular velocidades y tiempos para diferentes distancias
            tri_speeds = calculate_tri_speeds(
                ftp=ftp,
                mass_total=mass_total,  # Pasamos mass_total aquí
                cda=cda_value,
                rho=1.225,
                alpha=0.95
            )

            # Obtener etiqueta CdA
            cda_label = CDA_MAP.get(cda_value, "Desconocido")

            # Renderizar la página de resultados incluyendo tri_speeds
            return render_template(
                'cycling_results.html',
                ftp=round(ftp, 2),
                ftp_kg=round(ftp_kg, 2),
                category=category,
                zones=zones,
                velocidad_kmh=velocidad_kmh_100,
                cda_label=cda_label,
                cda_value=cda_value,
                mass_total=mass_total,
                tri_speeds=tri_speeds  # Agregamos tri_speeds aquí
            )
        except ValueError as e:
            return f"Error: {e}"

    # GET -> mostrar formulario
    return render_template('cycling_input.html')

# -------------------------------------------------------------------------------------
# RUTA 2: /ajustes_cycling
# Página con sliders para distancia, FTP, desnivel, etc.
# Recibe datos por GET (al hacer clic en "ESTRATEGIA") o por POST (form).
# -------------------------------------------------------------------------------------
@app.route('/ajustes_cycling', methods=['GET', 'POST'])
def ajustes_cycling():
    if request.method == 'POST':
        # Procesar datos enviados por formulario POST
        try:
            ftp = float(request.form.get('ftp', 300))
            desnivel_acumulado = float(request.form.get('desnivel_acumulado', 0))
            distancia_km = float(request.form.get('distancia_km', 20))
            intensidad_pct = float(request.form.get('intensidad_pct', 100))
            cda_value = float(request.form.get('cda_value', 0.25))
            mass_total = float(request.form.get('mass_total', 70))  # Valor por defecto de 70 kg
        except ValueError:
            return "Error: revisa campos numéricos."

        # Cálculo
        rho = 1.225  # Densidad del aire

        # Calcular potencia objetivo
        power_objetivo = ftp * (intensidad_pct / 100.0) 

        # Calcular velocidad en terreno plano
        speedFlat = calculate_corrected_speed(
            ftp=ftp,
            mass_total=mass_total,  # Asegurarse de pasar mass_total
            cda=cda_value,
            intensity=intensidad_pct / 100.0,
            rho=rho,
            alpha=0.95
        )

        # Calcular la pendiente media (%)
        pendienteMedia = desnivel_acumulado / distancia_km  # m/km = % pendiente media

        # Definir un coeficiente de reducción basado en la pendiente
        coefReduccion = 0.005  # 0.5% de reducción por cada 1% de pendiente

        # Ajustar la velocidad en función de la pendiente
        speedAdjusted = speedFlat * (1 - (pendienteMedia * coefReduccion))

        # Asegurar que la velocidad no sea negativa o demasiado baja
        finalSpeed = max(speedAdjusted, 5)  # Mínimo de 5 km/h

        # Calcular tiempo basado en la velocidad ajustada
        tiempo_horas = distancia_km / finalSpeed if finalSpeed > 0 and distancia_km > 0 else 0

        # Convertir tiempo a HH:MM:SS
        tiempo_hhmmss = hours_to_hms_str(tiempo_horas)

        # Calcular vatios por kg
        if mass_total > 0:
            vatios_kg = power_objetivo / mass_total
        else:
            vatios_kg = 0

        # Calcular velocidades y tiempos para diferentes distancias
        tri_speeds = calculate_tri_speeds(
            ftp=ftp,
            mass_total=mass_total,  # Pasamos mass_total aquí
            cda=cda_value,
            rho=rho,
            alpha=0.95
        )

        # Obtener etiqueta CdA
        cda_label = CDA_MAP.get(cda_value, "Desconocido")

        # Renderizar la plantilla de ajustes con los datos calculados
        return render_template(
            'ajustes_cycling.html',
            ftp=ftp,
            desnivel_acumulado=desnivel_acumulado,
            distancia_km=distancia_km,
            intensidad_pct=intensidad_pct,
            mass_total=mass_total,
            potencia_objetivo=power_objetivo,
            velocidad_estimada=round(finalSpeed, 2),
            tiempo_estimada=tiempo_hhmmss,
            tri_speeds=tri_speeds,
            cda_label=cda_label,
            cda_value=cda_value,
            vatios_kg=round(vatios_kg, 2)  # Añadimos vatios_kg
        )

    else:
        # Si GET, recoger parámetros de la URL
        ftp = request.args.get('ftp', default=300, type=float)
        cda = request.args.get('cda', default=0.25, type=float)
        distancia_km = request.args.get('distancia_km', default=20, type=float)
        desnivel_acumulado = request.args.get('desnivel_acumulado', default=0, type=float)
        mass_total = request.args.get('mass_total', default=70, type=float)  # Valor por defecto de 70 kg

        # Renderizar la plantilla con valores iniciales
        return render_template(
            'ajustes_cycling.html',
            ftp=ftp,
            cda_value=cda,
            distancia_km=distancia_km,
            desnivel_acumulado=desnivel_acumulado,
            mass_total=mass_total
        )



@app.route('/triatlon_results', methods=['POST'])
def triatlon_results():
    try:
        # 1. Recoger datos del formulario
        swim_distance = int(request.form['swim_distance'])
        swim_hours = int(request.form['swim_hours'])
        swim_minutes = int(request.form['swim_minutes'])
        swim_seconds = int(request.form['swim_seconds'])

        run_distance = float(request.form['run_distance'])
        run_hours = int(request.form['run_hours'])
        run_minutes = int(request.form['run_minutes'])
        run_seconds = int(request.form['run_seconds'])

        # Recoger datos de Transiciones (HH:MM:SS)
        transition_hours = int(request.form['transition_hours'])
        transition_minutes = int(request.form['transition_minutes'])
        transition_seconds = int(request.form['transition_seconds'])

        gender = request.form['gender']
        weight = float(request.form['weight'])
        power = int(request.form['power'])
        test_time = int(request.form['test_time'])
        event = request.form['event']

        # Recoger CdA y mapearlo a una etiqueta legible
        cda = float(request.form.get('cda', 0.25))
        cda_labels = {
            0.2: "(posición élite)",
            0.225: "(posición avanzada)",
            0.25: "(posición estándar)",
            0.275: "(posición poco aerodinámica)",
            0.3: "(sin posición aerodinámica)"
        }
        cda_label = cda_labels.get(cda, "Desconocido")

        # 2. Procesar datos de natación
        swim_time = f"{swim_hours:02}:{swim_minutes:02}:{swim_seconds:02}"
        estimated_times, css, css_category = estimate_swim_times(swim_distance, swim_time)

        event_distances = {"sprint": 750, "olympic": 1500, "half": 1900, "full": 3800}
        event_distance = event_distances.get(event)
        if not event_distance:
            raise ValueError("Evento no válido.")

        event_swim_time_seconds = sum(
            x * int(t) for x, t in zip([3600, 60, 1], estimated_times[event_distance]["time"].split(":"))
        )

        # 3. Procesar datos de ciclismo (cálculo FTP)
        ftp, ftp_kg = calculate_ftp(gender, weight, power, test_time)
        ftp_category = classify_ftp(ftp_kg, gender)
        watts_range = calculate_event_watts(ftp, event)

        # 4. Procesar datos de bicicleta y velocidad
        bike_weight = 8.0
        alpha = 0.95
        mass_total = weight + bike_weight

        velocidad_ciclismo_100 = calculate_corrected_speed(
            ftp=ftp,
            mass_total=mass_total,
            cda=cda,
            intensity=1.0,
            rho=1.225,
            alpha=alpha
        )

        tri_speeds_data = calculate_tri_speeds(
            ftp=ftp,
            mass_total=mass_total,
            cda=cda,
            rho=1.225,
            alpha=alpha
        )

        bike_time_avg_sec = (
            (tri_speeds_data[event]["time_min"] + tri_speeds_data[event]["time_max"]) / 2 * 60
        )

        # 5. Procesar datos de carrera
        run_time = f"{run_hours:02}:{run_minutes:02}:{run_seconds:02}"
        avg_pace_seconds = calculate_pace(run_distance, run_time)
        ua_pace_seconds = calculate_anaerobic_threshold(run_distance, run_time)

        avg_pace = convert_seconds_to_min_km(avg_pace_seconds)
        ua_pace = convert_seconds_to_min_km(ua_pace_seconds)

        running_data = {
            "pace": avg_pace,
            "anaerobic_threshold": ua_pace,
            "ua_category": classify_anaerobic_threshold(gender, ua_pace_seconds),
            "estimated_times": estimate_running_times(avg_pace_seconds, run_distance),
        }
        event_running_times = calculate_event_running_times(event, avg_pace_seconds)

        run_time_sec = sum(
            x * int(t) for x, t in zip([3600, 60, 1], event_running_times["event_time"].split(":"))
        )

        # 6. Procesar datos de transiciones
        transition_time_sec = transition_hours * 3600 + transition_minutes * 60 + transition_seconds

        # 7. Calcular tiempo total (incluyendo transiciones)
        total_time_avg_sec = event_swim_time_seconds + bike_time_avg_sec + run_time_sec + transition_time_sec
        total_time_avg_hhmmss = hours_to_hms_str(total_time_avg_sec / 3600)

        # 8. Guardar tiempos en session para ajustes posteriores
        session['original_times'] = {
            'natacion': event_swim_time_seconds,
            'ciclismo': bike_time_avg_sec,
            'carrera': run_time_sec
        }
        session['original_total_time'] = total_time_avg_sec

        return render_template(
            'triatlon_results.html',
            estimated_times=estimated_times,
            event_time_swim=estimated_times[event_distance]["time"],
            css=css,
            css_category=css_category,
            event_distance=event_distance,
            ftp=round(ftp, 2),
            ftp_kg=round(ftp_kg, 2),
            ftp_category=ftp_category,
            watts_range=watts_range,
            running_data=running_data,
            event_running_times=event_running_times,
            event=event,
            velocidad_ciclismo_100=round(velocidad_ciclismo_100, 2),
            tri_speeds_data=tri_speeds_data,
            cda_label=cda_label,
            total_time_avg=total_time_avg_hhmmss
        )
    except Exception as e:
        return f"Error: {e}"


@app.route('/ajustes_input', methods=['GET'])
def ajustes_input():
    # Renderiza el formulario de ajustes
    return render_template('ajustes_input.html')

def convert_seconds_to_hms(seconds):
    """
    Convierte segundos en formato hh:mm:ss.
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"



# Registrar filtro para convertir segundos a formato hh:mm:ss
app.jinja_env.filters['convert_seconds_to_hms'] = convert_seconds_to_hms

@app.route('/ajustes_results', methods=['GET', 'POST'])
def ajustes_variables():
    if request.method == 'POST':
        try:
            # Procesar tiempos base (convertir minutos a segundos)
            base_times = {
                "natacion": float(request.form.get('base_time_swim', '0')) * 60,
                "ciclismo": float(request.form.get('base_time_bike', '0')) * 60,
                "carrera": float(request.form.get('base_time_run', '0')) * 60,
            }

            # Procesar ajustes
            adjustments = {
                "natacion": {
                    "neopreno": float(request.form.get('swim_adjustments_neopreno', '0')),
                    "olas_mod": float(request.form.get('swim_adjustments_olas_mod', '0')),
                    "corriente": float(request.form.get('swim_adjustments_corriente', '0')),
                    "tecnica": float(request.form.get('swim_adjustments_tecnica', '0')),
                },
                "ciclismo": {
                    "viento_mod": float(request.form.get('bike_adjustments_viento_mod', '0')),
                    "desnivel": float(request.form.get('bike_adjustments_desnivel', '0')),
                    "asfalto": float(request.form.get('bike_adjustments_asfalto', '0')),
                },
                "carrera": {
                    "temperatura_calor": float(request.form.get('run_adjustments_temperatura_calor', '0')),
                    "superficie_trail": float(request.form.get('run_adjustments_superficie_trail', '0')),
                    "fatiga": float(request.form.get('run_adjustments_fatiga', '0')),
                    "hidratacion": float(request.form.get('run_adjustments_hidratacion', '0')),
                },
            }

            # Calcular tiempos ajustados
            adjusted_times = {
                "natacion": calculate_adjusted_time(base_times["natacion"], adjustments["natacion"]),
                "ciclismo": calculate_adjusted_time(base_times["ciclismo"], adjustments["ciclismo"]),
                "carrera": calculate_adjusted_time(base_times["carrera"], adjustments["carrera"]),
            }

            total_adjusted_time = sum(adjusted_times.values())
            modified_variables = {
                k: [var for var, val in adjustments[k].items() if val != 0]
                for k in adjustments
            }

            return render_template(
                'ajustes_resultados.html',
                original_times=base_times,
                adjusted_times=adjusted_times,
                total_adjusted_time=total_adjusted_time,
                original_total_time=sum(base_times.values()),
                modified_variables=modified_variables,
            )
        except Exception as e:
            return f"Error inesperado: {e}"

    return render_template('ajustes_input.html')




@app.route('/triatlon_input', methods=['GET', 'POST'])
def triatlon_input():
    if request.method == 'POST':
        return triatlon_results()
    return render_template('triatlon_input.html')


if __name__ == '__main__':
    app.run(debug=True)
