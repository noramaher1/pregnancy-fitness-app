DISCLAIMER = "General information only. This is not medical advice. Ask your midwife or doctor before changing your exercise routine."

RULES = {
    1: {
        "do": ["Walking", "Swimming", "Prenatal yoga", "Light strength training"],
        "avoid": ["Overheating", "Contact sports"],
    },
    2: {
        "do": ["Walking", "Swimming", "Prenatal yoga", "Light strength training"],
        "avoid": ["Lying flat on your back for long periods", "Activities with a high risk of falling"],
    },
    3: {
        "do": ["Walking", "Pelvic floor exercises", "Stretching", "Gentle swimming"],
        "avoid": ["Lying flat on your back for long periods", "High-intensity workouts"],
    },
}


def trimester(week: int) -> int:
    if week <= 13:
        return 1
    if week <= 27:
        return 2
    return 3
