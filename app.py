from flask import Flask, render_template, request
from utils.running import (
    calculate_pace,
    estimate_running_times,
    validate_time_format,
    calculate_anaerobic_threshold,
    classify_anaerobic_threshold,
    process_running_data
)
from utils.swimming import estimate_swim_times
from utils.cycling import calculate_ftp, classify_ftp, calculate_ftp_zones
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
    classify_anaerobic_threshold
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
        distance = float(request.form['distance'])
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

            # Renderizar los resultados
            return render_template(
                'running_results.html',
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

        # Calcular las estimaciones, CSS, categoría y zonas
        estimates, css, css_category, zones = estimate_swim_times(distance, total_time)

        # Renderizar resultados
        return render_template('swimming_results.html', estimates=estimates, css=css, css_category=css_category, zones=zones)

    # Renderizar el formulario si es un GET
    return render_template('swimming_input.html')

# Página para ciclismo
@app.route('/cycling', methods=['GET', 'POST'])
def cycling():
    if request.method == 'POST':
        gender = request.form['gender']
        weight = float(request.form['weight'])
        power = float(request.form['power'])
        test_time = int(request.form['test_time'])

        try:
            ftp, ftp_kg = calculate_ftp(gender, weight, power, test_time)
            category = classify_ftp(ftp_kg, gender)
            zones = calculate_ftp_zones(ftp)

            return render_template(
                'cycling_results.html',
                ftp=round(ftp, 2),
                ftp_kg=round(ftp_kg, 2),
                category=category,
                zones=zones
            )
        except ValueError as e:
            return f"Error: {e}"

    return render_template('cycling_input.html')


@app.route('/triatlon_results', methods=['POST'])
def triatlon_results():
    # Recoger datos del formulario
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

    # Procesar datos de natación
    swim_time = f"{swim_hours:02}:{swim_minutes:02}:{swim_seconds:02}"
    estimated_times, css, css_category = estimate_swim_times(swim_distance, swim_time)
    event_distances = {"sprint": 750, "olympic": 1500, "half": 1900, "full": 3800}
    event_distance = event_distances[event]
    event_swim_time = estimated_times[event_distance]

    # Procesar datos de ciclismo
    ftp, ftp_kg = calculate_ftp(gender, weight, power, test_time)
    ftp_category = classify_ftp(ftp_kg, gender)
    event_watts = calculate_event_watts(ftp, event)

    # Procesar datos de carrera
    run_time = f"{run_hours:02}:{run_minutes:02}:{run_seconds:02}"

    # Cálculo del ritmo promedio y del umbral anaeróbico
    avg_pace_seconds = calculate_pace(run_distance, run_time)
    ua_pace_seconds = calculate_anaerobic_threshold(run_distance, run_time)

    # Convertir a formato legible
    avg_pace = convert_seconds_to_min_km(avg_pace_seconds)
    ua_pace = convert_seconds_to_min_km(ua_pace_seconds)

    running_data = {
        "pace": avg_pace,
        "anaerobic_threshold": ua_pace,
        "ua_category": classify_anaerobic_threshold(gender, ua_pace_seconds),
        "estimated_times": estimate_running_times(avg_pace_seconds, run_distance),
    }
    event_running_times = calculate_event_running_times(event, avg_pace_seconds)

    # Renderizar la plantilla con todos los datos
    return render_template(
        'triatlon_results.html',
        css=css,
        css_category=css_category,
        event_time=event_swim_time,
        event_distance=event_distance,
        ftp=round(ftp, 2),
        ftp_kg=round(ftp_kg, 2),
        ftp_category=ftp_category,
        event_watts=event_watts,
        running_data=running_data,
        event_running_times=event_running_times,
        event=event
    )



@app.route('/triatlon_input', methods=['GET', 'POST'])
def triatlon_input():
    if request.method == 'POST':
        return triatlon_results()
    return render_template('triatlon_input.html')


if __name__ == '__main__':
    app.run(debug=True)