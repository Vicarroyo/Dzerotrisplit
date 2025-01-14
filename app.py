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

# Crear la instancia de Flask
app = Flask(__name__)

# Ruta de inicio
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



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

if __name__ == '__main__':
    app.run(debug=True)