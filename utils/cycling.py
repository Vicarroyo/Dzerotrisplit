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
        "Z4 (Umbral)": (ftp * 0.91, ftp * 1.05),
        "Z5 (VO2 máx)": (ftp * 1.06, ftp * 1.20),
        "Z6 (Capacidad anaeróbica)": (ftp * 1.21, ftp * 1.50),
        "Z7 (Potencia neuromuscular)": (ftp * 1.51, None),
    }
    return {k: (round(v[0], 2), round(v[1], 2) if v[1] else None) for k, v in zones.items()}
