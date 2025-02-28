def estimate_swim_times(distance, time):
    def convert_seconds_to_hms(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"

    def classify_css(css_seconds):
        if css_seconds < 75:
            return "Elite/Profesional"
        elif 75 <= css_seconds <= 85:
            return "Muy avanzado"
        elif 85 < css_seconds <= 100:
            return "Competitivo"
        elif 100 < css_seconds <= 115:
            return "Intermedio"
        else:
            return "Recreativo/Ritmos lentos"

    time_in_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], time.split(":")))

    target_distances = [50, 100, 200, 400, 750, 800, 1500, 1900, 3800, 5000]
    estimated_times = {}
    css_seconds = None

    for d in target_distances:
        estimated_time_seconds = time_in_seconds * (d / distance) ** 1.06
        pace_per_100m_seconds = estimated_time_seconds / (d / 100)
        estimated_times[d] = {
            "time": convert_seconds_to_hms(estimated_time_seconds),
            "pace_per_100m": convert_seconds_to_hms(pace_per_100m_seconds),
        }
        if d == 1500 or d == 1900:
            if css_seconds is None:
                css_seconds = pace_per_100m_seconds
            else:
                css_seconds = (css_seconds + pace_per_100m_seconds) / 2

    css = convert_seconds_to_hms(css_seconds) if css_seconds else None
    css_category = classify_css(css_seconds) if css_seconds else None


    return estimated_times, css, css_category


def calculate_ftp(gender, weight, power, test_time):
    """
    Calcula el FTP (Functional Threshold Power) y el FTP/kg en función de los vatios medios,
    el peso y la duración del test (10, 20 o 30 minutos).
    """
    if test_time == 10:
        ftp = power * 0.90
    elif test_time == 20:
        ftp = power * 0.95
    else:  # Test de 30 minutos
        ftp = power
    ftp_kg = ftp / weight  # Calcular FTP por kilogramo
    return ftp, ftp_kg

def classify_ftp(ftp_kg, gender):
    """
    Clasifica el FTP/kg en diferentes niveles según el género.
    """
    thresholds = {
        'male': [2.0, 3.5, 4.5, 5.5, 6.5],  # Umbrales para hombres
        'female': [1.8, 3.0, 4.0, 5.0, 6.0]  # Umbrales para mujeres
    }
    labels = ['Principiante', 'Intermedio', 'Avanzado', 'Experto', 'Élite nacional', 'Élite mundial']
    for i, threshold in enumerate(thresholds[gender]):
        if ftp_kg < threshold:
            return labels[i]
    return labels[-1]

def calculate_event_watts(ftp, event):
    """
    Calcula el rango de vatios estimados para el evento objetivo basados en el FTP y
    los porcentajes correspondientes según la distancia seleccionada.
    """
    event_adjustments = {
        'sprint': (0.95, 1.00),     # 100% del FTP
        'olympic': (0.90, 0.95),    # 95-100% del FTP
        'half': (0.85, 0.90),       # 90-95% del FTP
        'full': (0.75, 0.80)        # 80-85% del FTP
    }
    min_factor, max_factor = event_adjustments[event]
    min_watts = ftp * min_factor
    max_watts = ftp * max_factor
    return (round(min_watts, 2), round(max_watts, 2))



# Función para convertir segundos a formato legible min/km
def convert_seconds_to_min_km(pace_seconds):
    """
    Convierte segundos por km a formato legible (min/km).
    """
    minutes = int(pace_seconds // 60)
    seconds = int(pace_seconds % 60)
    return f"{minutes}:{seconds:02d} min/km"

# Función para convertir segundos a formato hh:mm:ss
def convert_seconds_to_hms(seconds):
    """
    Convierte segundos a formato hh:mm:ss.
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

# Función para calcular ritmo promedio 
def calculate_pace(distance, time):
    """
    Calcula el ritmo promedio (segundos por km) basado en la distancia y el tiempo.
    """
    time_parts = time.split(":")
    time_in_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    return time_in_seconds / distance

# Función para calcular el umbral anaeróbico
def calculate_anaerobic_threshold(distance, time):
    """
    Calcula el ritmo de Umbral Anaeróbico (UA) ajustado según el tiempo total de la carrera.
    """
    avg_pace_seconds = calculate_pace(distance, time)

    # Convertir tiempo a segundos totales para clasificar el factor
    time_parts = time.split(":")
    time_in_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    time_in_minutes = time_in_seconds / 60

    # Definir factores de ajuste basados en el tiempo total
    if time_in_minutes < 60:
        factor = 1.05  # Ajuste menor para tiempos por debajo de 60 minutos
    else:
        factor = 1.02  # Ajuste leve para tiempos por encima de 60 minutos

    # Calcular ritmo de umbral anaeróbico
    if time_in_minutes < 60:
        threshold_pace_seconds = avg_pace_seconds * factor  # Más lento que el promedio
    else:
        threshold_pace_seconds = avg_pace_seconds / factor  # Más rápido que el promedio

    # Ajustar para mantener dentro de rangos típicos según ejemplos dados
    if distance == 5 and threshold_pace_seconds > avg_pace_seconds * 1.08:
        threshold_pace_seconds = avg_pace_seconds * 1.08
    elif distance == 10 and threshold_pace_seconds > avg_pace_seconds * 1.07:
        threshold_pace_seconds = avg_pace_seconds * 1.07
    elif distance == 15 and threshold_pace_seconds > avg_pace_seconds * 1.06:
        threshold_pace_seconds = avg_pace_seconds * 1.06
    elif distance == 21.1 and threshold_pace_seconds > avg_pace_seconds * 1.05:
        threshold_pace_seconds = avg_pace_seconds * 1.05
    elif distance >= 42.195 and threshold_pace_seconds > avg_pace_seconds * 1.04:
        threshold_pace_seconds = avg_pace_seconds * 1.04

    return threshold_pace_seconds



# Clasificación del umbral anaeróbico
def classify_anaerobic_threshold(gender, ua_pace):
    """
    Clasifica el nivel basado en el ritmo de Umbral Anaeróbico (UA) y género.
    """
    pace_min_km = ua_pace / 60  # Convertir a min/km

    if gender == "male":
        if pace_min_km < 3.25:
            return "Elite"
        elif 3.25 <= pace_min_km < 3.75:
            return "Avanzado"
        elif 3.75 <= pace_min_km < 4.5:
            return "Intermedio"
        elif 4.5 <= pace_min_km < 5.5:
            return "Principiante"
        else:
            return "Iniciación"
    elif gender == "female":
        if pace_min_km < 3.67:
            return "Elite"
        elif 3.67 <= pace_min_km < 4.17:
            return "Avanzado"
        elif 4.17 <= pace_min_km < 5.0:
            return "Intermedio"
        elif 5.0 <= pace_min_km < 6.0:
            return "Principiante"
        else:
            return "Iniciación"
    else:
        raise ValueError("Género inválido. Use 'male' o 'female'.")

# Procesar datos de carrera
def process_running_data(distance, time, gender):
    """
    Procesa los datos de carrera y devuelve los cálculos necesarios para los resultados.
    """
    avg_pace_seconds = calculate_pace(distance, time)
    anaerobic_threshold_seconds = calculate_anaerobic_threshold(distance, time)
    ua_category = classify_anaerobic_threshold(gender, anaerobic_threshold_seconds)
    
    return {
        "pace": convert_seconds_to_min_km(avg_pace_seconds),
        "anaerobic_threshold": convert_seconds_to_min_km(anaerobic_threshold_seconds),
        "ua_category": ua_category,
    }

def calculate_event_running_times(event, anaerobic_threshold_pace):
    """
    Calcula el tiempo y ritmo estimados para un evento objetivo basado en el umbral anaeróbico.

    Args:
        event (str): Tipo de evento ('sprint', 'olympic', 'half', 'full').
        anaerobic_threshold_pace (float): Ritmo de umbral anaeróbico (en segundos por kilómetro).

    Returns:
        dict: Tiempos y ritmos estimados para la distancia objetivo.
    """
    event_distances = {
        "sprint": 5,  # 5 km
        "olympic": 10,  # 10 km
        "half": 21.1,  # 21.1 km
        "full": 42.195,  # 42.195 km
    }

    adjustment_factors = {
        "sprint": 1,  # 100%
        "olympic": 1.025,  # 105%
        "half": 1.08,  # 110%
        'full': 1.18,  # 120%
    }

    # Validación de datos
    distance = event_distances.get(event)
    factor = adjustment_factors.get(event)
    if distance is None or factor is None:
        raise ValueError(f"Evento objetivo inválido: {event}")

    # Calcular ritmo ajustado y tiempo estimado
    adjusted_pace = anaerobic_threshold_pace * factor
    estimated_time_seconds = adjusted_pace * distance

    # Convertir ritmo y tiempo a formatos legibles
    estimated_time = convert_seconds_to_hms(estimated_time_seconds)
    estimated_pace = convert_seconds_to_min_km(adjusted_pace)

    return {
        "event_time": estimated_time,
        "event_pace": estimated_pace,
    }

def estimate_running_times(pace, base_distance):
    """
    Estima los tiempos de carrera y ritmos por km en otras distancias usando la fórmula de Jack Daniels.
    """
    distances = [5, 10, 15, 21.1, 42.195]
    results = {}

    factors = {
        5: 1.07,
        10: 1.06,
        15: 1.055,
        21.1: 1.05,
        42.195: 1.045,
    }

    for d in distances:
        k = factors[d]
        estimated_time = pace * base_distance * (d / base_distance) ** k  # Tiempo total en segundos
        estimated_pace = estimated_time / d  # Ritmo promedio en segundos por km
        results[d] = {
            "time": convert_seconds_to_hms(estimated_time),
            "pace": convert_seconds_to_hms(estimated_pace),
        }

    return results

def calculate_speed(ftp_kg, cyclist_weight, bike_weight, cda, rho=1.225):
    """
    Calcula la velocidad en km/h en llano (aerodinámica pura) a partir de:
      - ftp_kg: FTP relativo (W/kg)
      - cyclist_weight: peso del ciclista (kg)
      - bike_weight: peso de la bici (kg)
      - cda: coeficiente CdA
      - rho: densidad del aire (1.225 kg/m^3 por defecto)
    """
    total_mass = cyclist_weight + bike_weight
    p_total = ftp_kg * total_mass  # W
    v_ms = ((2.0 * p_total) / (rho * cda)) ** (1.0/3.0)  # en m/s
    v_kmh = 3.6 * v_ms
    return v_kmh

def calculate_corrected_speed(
    ftp,         # FTP absoluto (W)
    mass_total,  # ciclista + bici (kg)
    cda,         # CdA
    intensity=1.0,     # fracción del FTP (por ej. 0.95 para 95%)
    rho=1.225,         # densidad del aire
    alpha=0.95         # factor de corrección empírico (<1)
):
    """
    Calcula la velocidad en km/h para un % dado de FTP, asumiendo llano,
    sin viento, y aplicando un factor de corrección alpha para rodadura/pérdidas.
    """
    # 1) Potencia efectiva según el % de FTP
    p_eff = ftp * intensity  # W

    # 2) Vel. teórica (fórmula aerodinámica pura)
    #    P = 1/2 * rho * CdA * v^3  =>  v = (2 * P / (rho * CdA))^(1/3)
    v_ms = ((2.0 * p_eff) / (rho * cda)) ** (1.0 / 3.0)
    v_kmh_theoretical = v_ms * 3.6

    # 3) Aplicar factor de corrección
    v_kmh_corrected = v_kmh_theoretical * alpha

    return v_kmh_corrected

# Definir la función para convertir segundos a hh:mm:ss
def convert_seconds_to_hms(seconds):
    """
    Convierte segundos a formato hh:mm:ss.
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

def hours_to_hms_str(hours):
    """
    Convierte un número de horas en string formato hh:mm:ss
    """
    total_seg = int(hours * 3600)  # total de segundos
    hh = total_seg // 3600
    mm = (total_seg % 3600) // 60
    ss = total_seg % 60
    # Formato con dos dígitos para horas, minutos y segundos:
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

def calculate_adjusted_time(base_time, adjustments):
    adjusted_time = base_time
    for adjustment in adjustments.values():
        adjusted_time *= 1 + (adjustment / 100)
    return adjusted_time

def calculate_tri_speeds(ftp, mass_total, cda, rho=1.225, alpha=0.95):
    tri_data = {
        "sprint": {
            "int_range": (0.9, 1.0),
            "distance_km": 20
        },
        "olympic": {
            "int_range": (0.80, 0.9),
            "distance_km": 40
        },
        "half": {
            "int_range": (0.70, 0.8),
            "distance_km": 90
        },
        "full": {
            "int_range": (0.60, 0.7),
            "distance_km": 180
        }
    }

    results = {}
    for dist_name, data in tri_data.items():
        int_min, int_max = data["int_range"]
        distance = data["distance_km"]

        v_min = calculate_corrected_speed(ftp, mass_total, cda, int_min, rho, alpha)
        v_max = calculate_corrected_speed(ftp, mass_total, cda, int_max, rho, alpha)

        time_min_h = distance / v_max
        time_max_h = distance / v_min

        time_min_min = time_min_h * 60
        time_max_min = time_max_h * 60

        # Aquí usamos la función hours_to_hms_str
        time_min_hhmmss = hours_to_hms_str(time_min_h)
        time_max_hhmmss = hours_to_hms_str(time_max_h)

        results[dist_name] = {
            "v_min": v_min,
            "v_max": v_max,
            "time_min": time_min_min,      # en minutos
            "time_max": time_max_min,      # en minutos
            "time_min_hhmmss": time_min_hhmmss,
            "time_max_hhmmss": time_max_hhmmss
        }
    return results





