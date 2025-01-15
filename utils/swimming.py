def estimate_swim_times(distance, time):
    """
    Calcula los tiempos estimados para varias distancias en natación basados en la fórmula de Peter Riegel,
    incluye el ritmo promedio por 100 metros para cada distancia objetivo y el cálculo del CSS.
    """
    def convert_seconds_to_hms(seconds):
        """
        Convierte segundos a formato hh:mm:ss.
        """
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"
    
    def classify_css(css_seconds):
        """
        Clasifica el CSS (en segundos por 100m) en una categoría.
        """
        if css_seconds < 75:  # <1:15/100m
            return "Elite/Profesional"
        elif 75 <= css_seconds <= 85:  # 1:15-1:25/100m
            return "Muy avanzado"
        elif 85 < css_seconds <= 100:  # 1:25-1:40/100m
            return "Competitivo"
        elif 100 < css_seconds <= 115:  # 1:40-1:55/100m
            return "Intermedio"
        else:  # >1:55/100m
            return "Recreativo/Ritmos lentos"

    try:
        # Convertir tiempo a segundos
        time_in_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], time.split(":")))
        if time_in_seconds <= 0:
            raise ValueError("El tiempo debe ser mayor que cero.")
    except ValueError:
        raise ValueError("El tiempo debe estar en el formato hh:mm:ss.")

    # Distancias objetivo
    target_distances = [50, 100, 200, 400, 800, 1500, 1900, 3800, 5000]
    
    # Calcular los tiempos estimados y ritmos usando la fórmula de Peter Riegel
    estimated_times = {}
    css_seconds = None  # Variable para almacenar el CSS en segundos
    for d in target_distances:
        estimated_time_seconds = time_in_seconds * (d / distance) ** 1.06
        pace_per_100m_seconds = estimated_time_seconds / (d / 100)
        estimated_times[d] = {
            "time": convert_seconds_to_hms(estimated_time_seconds),
            "pace_per_100m": convert_seconds_to_hms(pace_per_100m_seconds),
        }
        # Capturar el ritmo CSS del rango 1500m - 1900m
        if d == 1500 or d == 1900:
            if css_seconds is None:
                css_seconds = pace_per_100m_seconds
            else:
                css_seconds = (css_seconds + pace_per_100m_seconds) / 2

    # Convertir el CSS a formato hh:mm:ss y clasificar
    css = convert_seconds_to_hms(css_seconds) if css_seconds else None
    css_category = classify_css(css_seconds) if css_seconds else None

    return estimated_times, css, css_category

def calculate_zones(css_seconds):
    """
    Calcula los rangos de tiempo para cada zona en base al CSS.
    """
    def convert_seconds_to_hms(seconds):
        """
        Convierte segundos a formato hh:mm:ss.
        """
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"

    zones = {
        "Zona 1 – Recuperación activa": (0, 1.16 * css_seconds),
        "Zona 2 – Resistencia aeróbica": (1.16 * css_seconds, 1.08 * css_seconds),
        "Zona 3 – Umbral aeróbico": (1.08 * css_seconds, 1.04 * css_seconds),
        "Zona 4 – Umbral anaeróbico": (1.04 * css_seconds, 0.98 * css_seconds),
        "Zona 5 – Velocidad": (0.98 * css_seconds, 0.90 * css_seconds),
        "Zona 6 – Esfuerzo máximo": (0.90 * css_seconds, float('inf')),
    }

    # Convertir los rangos a formato hh:mm:ss
    zones_converted = {
        zone: (convert_seconds_to_hms(min_val), convert_seconds_to_hms(max_val if max_val != float('inf') else 3600))
        for zone, (min_val, max_val) in zones.items()
    }
    return zones_converted
