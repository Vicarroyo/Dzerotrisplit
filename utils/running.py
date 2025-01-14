import math

def calculate_anaerobic_threshold(distance, time):
    """
    Calcula el ritmo de Umbral Anaeróbico (UA) basado en un ajuste porcentual.
    Fórmula: R_UA = R_avg * (1 + porcentaje_incremento)

    Args:
        distance (float): Distancia en kilómetros.
        time (str): Tiempo en formato hh:mm:ss.

    Returns:
        str: Ritmo de Umbral Anaeróbico (min/km) en formato legible.
    """
    try:
        # Definir el porcentaje de incremento basado en la distancia
        if distance <= 5:
            porcentaje_incremento = 0.05
        elif distance <= 10:
            porcentaje_incremento = 0.04
        elif distance <= 15:
            porcentaje_incremento = 0.03
        elif distance <= 21.1:
            porcentaje_incremento = 0.02
        else:
            porcentaje_incremento = 0.01

        # Convertir tiempo a segundos
        time_parts = time.split(":")
        time_in_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])

        # Calcular ritmo promedio en segundos por kilómetro
        avg_pace = time_in_seconds / distance

        # Aplicar el ajuste porcentual para calcular el ritmo de UA
        ua_pace = avg_pace * (1 + porcentaje_incremento)

        # Convertir el ritmo de UA a formato legible (min/km)
        minutes = int(ua_pace // 60)
        seconds = int(ua_pace % 60)

        return f"{minutes}:{seconds:02d} min/km"
    except Exception as e:
        raise ValueError(f"Error al calcular el Umbral Anaeróbico: {e}")

def classify_anaerobic_threshold(gender, ua_pace):
    """
    Clasifica el nivel basado en el ritmo de Umbral Anaeróbico (UA) y género.

    Args:
        gender (str): 'male' para hombres, 'female' para mujeres.
        ua_pace (float): Ritmo de UA en segundos por km.

    Returns:
        str: Nivel clasificado (Elite, Avanzado, etc.).
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

def calculate_pace_zones_joe_friel(anaerobic_threshold):
    """
    Calcula las zonas de ritmo basadas en porcentajes del ritmo de Umbral Anaeróbico (UA) usando la fórmula de Joe Friel.
    """
    zones = {
        "Zona 1 – Recuperación activa": (anaerobic_threshold * 1.30, anaerobic_threshold * 1.35),
        "Zona 2 – Resistencia aeróbica": (anaerobic_threshold * 1.16, anaerobic_threshold * 1.30),
        "Zona 3 – Tempo": (anaerobic_threshold * 1.06, anaerobic_threshold * 1.16),
        "Zona 4 – Umbral anaeróbico": (anaerobic_threshold * 1.03, anaerobic_threshold * 1.06),
        "Zona 5 – Velocidad": (anaerobic_threshold * 0.96, anaerobic_threshold * 1.03),
        "Zona 6 – Esfuerzo máximo": (anaerobic_threshold * 0.96, float('inf')),
    }

    # Convertir los rangos a formato legible
    zones_converted = {
        zone: (
            convert_seconds_to_hms(min_val) if min_val > 0 else "N/A",
            convert_seconds_to_hms(max_val) if max_val != float('inf') else "∞",
        )
        for zone, (min_val, max_val) in zones.items()
    }
    return zones_converted

def estimate_running_times(pace, base_distance):
    """
    Estima los tiempos de carrera y ritmos por km en otras distancias usando la fórmula de Jack Daniels.
    """
    distances = [5, 10, 15, 21.1, 42.195]  # Distancias objetivo en km
    results = {}

    # Factores de ajuste
    factors = {
        5: 1.07,
        10: 1.07,
        15: 1.06,
        21.1: 1.06,
        42.195: 1.06,
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

def process_running_data(distance, time, gender):
    """
    Procesa los datos de carrera y devuelve los cálculos necesarios para los resultados.
    """
    pace = calculate_pace(distance, time)
    anaerobic_threshold = calculate_anaerobic_threshold(distance, time)
    ua_pace_seconds = calculate_pace(distance, time) * 1.05  # Ajuste para UA en segundos
    ua_category = classify_anaerobic_threshold(gender, ua_pace_seconds)
    estimated_times = estimate_running_times(pace, distance)
    zones = calculate_pace_zones_joe_friel(pace)

    return {
        "pace": convert_seconds_to_hms(pace),
        "anaerobic_threshold": anaerobic_threshold,
        "ua_category": ua_category,
        "estimated_times": estimated_times,
        "zones": zones,
    }

def calculate_pace(distance, time):
    """
    Calcula el ritmo base (segundos por km).
    """
    time_parts = time.split(":")
    time_in_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    pace = time_in_seconds / distance  # Segundos por km
    return pace

def convert_seconds_to_hms(seconds):
    """
    Convierte segundos a formato hh:mm:ss.
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

def validate_time_format(time):
    """
    Verifica si el tiempo tiene el formato hh:mm:ss válido.
    """
    try:
        parts = time.split(":")
        if len(parts) != 3:
            raise ValueError("El tiempo debe tener el formato hh:mm:ss.")
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        if h < 0 or m < 0 or s < 0 or m >= 60 or s >= 60:
            raise ValueError("Valores de tiempo inválidos.")
        return True
    except Exception as e:
        raise ValueError(f"Formato de tiempo inválido: {e}")
