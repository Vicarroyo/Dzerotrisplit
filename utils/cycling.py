def calculate_ftp(gender, weight, power, test_time):
    if test_time == 10:
        ftp = power * 0.90
    elif test_time == 20:
        ftp = power * 0.95
    else:
        ftp = power
    ftp_kg = ftp / weight
    return ftp, ftp_kg

def classify_ftp(ftp_kg, gender):
    thresholds = {
        'male': [2.0, 3.5, 4.5, 5.5, 6.5],
        'female': [1.8, 3.0, 4.0, 5.0, 6.0]
    }
    labels = ['Principiante', 'Intermedio', 'Avanzado', 'Experto', 'Élite nacional', 'Élite mundial']
    for i, threshold in enumerate(thresholds[gender]):
        if ftp_kg < threshold:
            return labels[i]
    return labels[-1]

def calculate_ftp_zones(ftp):
    zones = {
        "Z1 (Recuperación activa)": (0, ftp * 0.55),
        "Z2 (Resistencia)": (ftp * 0.55, ftp * 0.75),
        "Z3 (Tempo)": (ftp * 0.76, ftp * 0.90),
        "Z4 (Umbral anaeróbico)": (ftp * 0.91, ftp * 1.05),
        "Z5 (VO2 máx)": (ftp * 1.06, ftp * 1.20),
        "Z6 (Capacidad anaeróbica)": (ftp * 1.21, ftp * 1.50),
        "Z7 (Potencia neuromuscular)": (ftp * 1.51, None),
    }
    return {k: (round(v[0], 2), round(v[1], 2) if v[1] else None) for k, v in zones.items()}

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



def calculate_tri_speeds(ftp, mass_total, cda, rho=1.225, alpha=0.95):
    tri_data = {
        "Sprint ": {
            "int_range": (0.9, 1.00),
            "distance_km": 20
        },
        "Olímpico ": {
            "int_range": (0.80, 0.9),
            "distance_km": 40
        },
        "Half ": {
            "int_range": (0.70, 0.8),
            "distance_km": 90
        },
        "Full ": {
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
