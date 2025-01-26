import math

def calculate_pace(distance, time):
    """Calcula el ritmo promedio (segundos por km) basado en la distancia y el tiempo."""
    h, m, s = map(int, time.split(":"))
    time_in_seconds = h * 3600 + m * 60 + s
    return time_in_seconds / distance

def convert_seconds_to_hms(seconds):
    """Convierte segundos a formato hh:mm:ss."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"

def calculate_anaerobic_threshold_riegel(distance_km, time_hms):
    """
    Calcula el ritmo de Umbral Anaeróbico, asumiendo que UA equivale al ritmo
    para 60 minutos, usando la fórmula de Riegel.
    """
    # 1) Convertimos el tiempo del test a minutos
    h, m, s = map(int, time_hms.split(":"))
    total_minutes = h * 60 + m + s / 60.0

    # 2) Distancia esperable en 60 min (D2)
    distance_60 = distance_km * (60.0 / total_minutes) ** (1.0 / 1.06)

    # 3) Ritmo (min/km)
    pace_min_km = 60.0 / distance_60

    # 4) Convertimos a mm:ss
    pace_minutes = int(pace_min_km)
    pace_seconds = round((pace_min_km - pace_minutes) * 60)
    if pace_seconds == 60:
        pace_seconds = 0
        pace_minutes += 1

    return f"{pace_minutes:02}:{pace_seconds:02}:00"

# Ejemplo de uso
distance_test = 15  # km
time_test = "00:46:00"

ua_estimate = calculate_anaerobic_threshold_riegel(distance_test, time_test)
print("Umbral Anaeróbico estimado (Riegel):", ua_estimate, "min/km")


# Función para calcular el umbral anaeróbico
def calculate_anaerobic_threshold(distance_km, time_hms):
    """
    Calcula el ritmo de Umbral Anaeróbico basado en el tiempo del test y la distancia.
    Devuelve el ritmo en minutos por km.
    """
    # Convertir tiempo del test a minutos
    h, m, s = map(int, time_hms.split(":"))
    total_minutes = h * 60 + m + s / 60.0

    # Calcular distancia equivalente en 60 minutos usando la fórmula de Riegel
    factor_riegel = 1.06
    distance_60 = distance_km * (60.0 / total_minutes) ** (1.0 / factor_riegel)

    # Calcular ritmo (min/km)
    pace_min_km = 60.0 / distance_60

    # Convertir a formato mm:ss
    pace_minutes = int(pace_min_km)
    pace_seconds = round((pace_min_km - pace_minutes) * 60)
    if pace_seconds == 60:
        pace_seconds = 0
        pace_minutes += 1

    return f"{pace_minutes:02}:{pace_seconds:02}"

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

def convert_time_to_seconds(time_hms):
    """
    Convierte un tiempo en formato hh:mm:ss o mm:ss a segundos.
    """
    parts = time_hms.split(":")
    if len(parts) == 2:  # Formato mm:ss
        m, s = map(int, parts)
        return m * 60 + s
    elif len(parts) == 3:  # Formato hh:mm:ss
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
    else:
        raise ValueError("El formato de tiempo debe ser hh:mm:ss o mm:ss.")

def calculate_pace_zones_joe_friel(anaerobic_threshold_pace_seconds):
    """
    Calcula las zonas de ritmo basadas en porcentajes del ritmo de Umbral Anaeróbico (UA) según Joe Friel.

    Args:
        anaerobic_threshold_pace_seconds (float): Ritmo del Umbral Anaeróbico (en segundos por km).

    Returns:
        dict: Zonas de ritmo con rangos en formato hh:mm:ss por km.
    """
    zones = {
        "Zona 1 – Recuperación activa": (anaerobic_threshold_pace_seconds * 1.29, anaerobic_threshold_pace_seconds * 1.35),
        "Zona 2 – Umbral aeróbico": (anaerobic_threshold_pace_seconds * 1.14, anaerobic_threshold_pace_seconds * 1.29),
        "Zona 3 – Tempo": (anaerobic_threshold_pace_seconds * 1.02, anaerobic_threshold_pace_seconds * 1.14),
        "Zona 4 – Umbral anaeróbico": (anaerobic_threshold_pace_seconds * 0.99, anaerobic_threshold_pace_seconds * 1.02),
        "Zona 5 – Supraumbral": (anaerobic_threshold_pace_seconds * 0.92, anaerobic_threshold_pace_seconds * 0.99),
        "Zona 6 – Velocidad aeróbica máxima": (anaerobic_threshold_pace_seconds * 0.92, float('inf')),
    }

    # Convertir los rangos de segundos/km a formato hh:mm:ss
    converted_zones = {
        zone: (convert_seconds_to_hms(rango[0]), convert_seconds_to_hms(rango[1]) if rango[1] != float('inf') else "∞")
        for zone, rango in zones.items()
    }

    return converted_zones

def process_running_data(distance, time, gender):
    """
    Procesa los datos de carrera y devuelve los cálculos necesarios para los resultados.
    """
    pace = calculate_pace(distance, time)  # Ritmo promedio en segundos por km
    anaerobic_threshold = calculate_anaerobic_threshold(distance, time)  # UA en formato mm:ss/km
    anaerobic_threshold_seconds = convert_time_to_seconds(anaerobic_threshold)  # Convertir UA a segundos por km
    ua_category = classify_anaerobic_threshold(gender, anaerobic_threshold_seconds)  # Clasificación
    estimated_times = estimate_running_times(pace, distance)  # Tiempos estimados para otras distancias
    
    # Calcular zonas de ritmo según Joe Friel
    zones = calculate_pace_zones_joe_friel(anaerobic_threshold_seconds)

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
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"

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
