from flask import Flask, render_template, request
from utils.running import (
    calculate_pace,
    estimate_running_times,
    validate_time_format,
    calculate_anaerobic_threshold,
    classify_anaerobic_threshold,
    process_running_data
)
from utils.swimming import estimate_swim_times, calculate_zones
from utils.cycling import calculate_ftp, classify_ftp, calculate_ftp_zones, calculate_corrected_speed, calculate_tri_speeds
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
    calculate_tri_speeds
)


# Crear la instancia de Flask
app = Flask(__name__)

# Ruta de inicio
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/plans')
def plans():
    return render_template('planes.html')



# Página para carrera
@app.route('/running', methods=['GET', 'POST'])
def running():
    if request.method == 'POST':
        distance = float(request.form['distance'])  # Obtener distancia del formulario
        gender = request.form['gender']
        hours = int(request.form['hours'])
        minutes = int(request.form['minutes'])
        seconds = int(request.form['seconds'])

        # Convertir tiempo a formato hh:mm:ss
        time = f"{hours:02}:{minutes:02}:{seconds:02}"

        try:
            # Validar el formato del tiempo
            validate_time_format(time)

            # Procesar los datos de carrera
            results = process_running_data(distance, time, gender)

            # Renderizar los resultados y pasar la distancia al template
            return render_template(
                'running_results.html',
                selected_distance=distance,  # Pasar la distancia seleccionada al template
                pace=results["pace"],
                anaerobic_threshold=results["anaerobic_threshold"],
                ua_category=results["ua_category"],
                estimated_times=results["estimated_times"],
                zones=results["zones"],
            )
        except ValueError as e:
            return f"Error: {e}"

    return render_template('running_input.html')



# Página para natación
@app.route('/swimming', methods=['GET', 'POST']) 
def swimming():
    if request.method == 'POST':
        # Obtener los datos del formulario
        distance = float(request.form['distance'])
        hours = int(request.form['hours'])
        minutes = int(request.form['minutes'])
        seconds = int(request.form['seconds'])

        # Convertir tiempo a formato hh:mm:ss
        total_time = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Calcular las estimaciones, CSS y categoría
        estimates, css, css_category = estimate_swim_times(distance, total_time)

        # Calcular las zonas en base al CSS
        css_seconds = sum(
            x * int(t) for x, t in zip([3600, 60, 1], css.split(":"))
        )  # Convertir CSS a segundos
        zones = calculate_zones(css_seconds)

        # Calcular ritmo promedio (pace) en segundos por 100m
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        pace_seconds = (total_seconds / distance) * 100  # Tiempo por 100m
        pace_minutes = int(pace_seconds // 60)
        pace_remainder_seconds = int(pace_seconds % 60)
        pace = f"{pace_minutes:02}:{pace_remainder_seconds:02}"  # Formato mm:ss

        # Renderizar resultados
        return render_template(
            'swimming_results.html',
            selected_distance=distance,
            pace=pace,
            estimates=estimates,
            css=css,
            css_category=css_category,
            zones=zones,
        )

    # Renderizar el formulario si es un GET
    return render_template('swimming_input.html')


from flask import render_template, request

# Diccionario para mapear valor CdA a etiqueta
CDA_MAP = {
    0.2:   "posición élite",
    0.225: "posición avanzada",
    0.25:  "posición estándar",
    0.275: "posición poco aerodinámica",
    0.3:   "sin posición aerodinámica"
}

@app.route('/cycling', methods=['GET', 'POST'])
def cycling():
    if request.method == 'POST':
        gender = request.form['gender']
        weight = float(request.form['weight'])           # Peso del ciclista
        bike_weight = float(request.form['bike_weight']) # Peso de la bici
        power = float(request.form['power'])             # Vatios NP
        test_time = int(request.form['test_time'])
        cda_value = float(request.form['cda'])           # CdA numérico

        try:
            # 1) Calcular FTP y FTP relativo
            ftp, ftp_kg = calculate_ftp(gender, weight, power, test_time)
            category = classify_ftp(ftp_kg, gender)
            zones = calculate_ftp_zones(ftp)

            # Masa total
            mass_total = weight + bike_weight

            # 2) Factor de corrección (ejemplo: 0.95)
            alpha = 0.95

            # 3) Velocidad (al 100% de FTP)
            velocidad_kmh_100 = calculate_corrected_speed(
                ftp=ftp,
                mass_total=mass_total,
                cda=cda_value,
                intensity=1.0,    # 100% FTP
                rho=1.225,
                alpha=alpha
            )
            velocidad_kmh_100 = round(velocidad_kmh_100, 2)

            # 4) Velocidades para diferentes distancias (según %FTP)
            tri_speeds = calculate_tri_speeds(
                ftp=ftp,
                mass_total=mass_total,
                cda=cda_value,
                rho=1.225,
                alpha=alpha
            )

            # Redondeamos v_min, v_max, time_min, time_max
            for dist_name, info in tri_speeds.items():
                info["v_min"] = round(info["v_min"], 2)
                info["v_max"] = round(info["v_max"], 2)
                info["time_min"] = round(info["time_min"], 1)
                info["time_max"] = round(info["time_max"], 1)

            # 5) Obtener etiqueta CdA
            cda_label = CDA_MAP.get(cda_value, "desconocido")

            # 6) Renderizar la plantilla con todos los datos
            return render_template(
                'cycling_results.html',
                ftp=round(ftp, 2),
                ftp_kg=round(ftp_kg, 2),
                category=category,
                zones=zones,
                velocidad_kmh=velocidad_kmh_100,  # Vel. al 100% FTP
                tri_speeds=tri_speeds,            # Info de distancias
                cda_label=cda_label               # CdA descriptivo
            )
        except ValueError as e:
            return f"Error: {e}"

    # Si GET, mostrar el formulario de entrada
    return render_template('cycling_input.html')

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

        gender = request.form['gender']
        weight = float(request.form['weight'])
        power = int(request.form['power'])
        test_time = int(request.form['test_time'])
        event = request.form['event']

        # Recoger CdA y mapearlo a una etiqueta legible
        cda = float(request.form.get('cda', 0.25))  # Default a 0.25 si no se proporciona
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
        bike_weight = 8.0  # Peso de la bicicleta en kg
        alpha = 0.95  # Factor de corrección empírico
        mass_total = weight + bike_weight

        # Velocidad al 100% de FTP (teórica + corrección)
        velocidad_ciclismo_100 = calculate_corrected_speed(
            ftp=ftp,
            mass_total=mass_total,
            cda=cda,
            intensity=1.0,  # 100% FTP
            rho=1.225,
            alpha=alpha
        )

        # Velocidades y tiempos por tipo de evento
        tri_speeds_data = calculate_tri_speeds(
            ftp=ftp,
            mass_total=mass_total,
            cda=cda,
            rho=1.225,
            alpha=alpha
        )

        # Calcular el tiempo promedio de ciclismo en segundos
        bike_time_avg_sec = (
            tri_speeds_data[event]["time_min"] + tri_speeds_data[event]["time_max"]
        ) / 2 * 60

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

        # Tiempo total de carrera en segundos
        run_time_sec = sum(
            x * int(t) for x, t in zip([3600, 60, 1], event_running_times["event_time"].split(":"))
        )

        # 6. Calcular tiempo total promedio
        total_time_avg_sec = event_swim_time_seconds + bike_time_avg_sec + run_time_sec
        total_time_avg_hhmmss = hours_to_hms_str(total_time_avg_sec / 3600)

        # 7. Renderizar la plantilla con todos los datos
        return render_template(
            'triatlon_results.html',
            estimated_times=estimated_times,  # Pasar al contexto
            event_time_swim=estimated_times[event_distance]["time"],  # Tiempo específico de natación
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



@app.route('/triatlon_input', methods=['GET', 'POST'])
def triatlon_input():
    if request.method == 'POST':
        return triatlon_results()
    return render_template('triatlon_input.html')

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')



if __name__ == '__main__':
    app.run(debug=True)
