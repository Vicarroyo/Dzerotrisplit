import math

# Función para calcular ritmo promedio 
def calculate_pace(distance, time):
    """
    Calcula el ritmo promedio (segundos por km) basado en la distancia y el tiempo.
    """
    time_parts = time.split(":")
    time_in_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    return time_in_seconds / distance

# Función para convertir segundos a hh:mm:ss
def convert_seconds_to_hms(seconds):
    """
    Convierte segundos a formato hh:mm:ss.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"

# Función para calcular el umbral anaeróbico
def calculate_anaerobic_threshold(distance, time):
    """
    Calcula el ritmo de Umbral Anaeróbico (UA) ajustado según el tiempo total de la carrera.
    Devuelve el ritmo en formato hh:mm:ss por km.
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

    return convert_seconds_to_hms(threshold_pace_seconds)


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
        "Zona 2 – Umbral aeróbico": (anaerobic_threshold * 1.16, anaerobic_threshold * 1.30),
        "Zona 3 – Tempo": (anaerobic_threshold * 1.06, anaerobic_threshold * 1.16),
        "Zona 4 – Umbral anaeróbico": (anaerobic_threshold * 1.03, anaerobic_threshold * 1.06),
        "Zona 5 – Supraumbral": (anaerobic_threshold * 0.96, anaerobic_threshold * 1.03),
        "Zona 6 – Velocidad aeróbica máxima": (anaerobic_threshold * 0.96, float('inf')),
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

# Función para calcular ritmo promedio 
def calculate_pace(distance, time):
    """
    Calcula el ritmo promedio (segundos por km) basado en la distancia y el tiempo.
    """
    time_parts = time.split(":")
    time_in_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    return time_in_seconds / distance

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

