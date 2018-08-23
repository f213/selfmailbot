LANGUAGES = (
    ('ru-RU', 'Russian'),
    ('en', 'English'),
)


def get_languages():
    return LANGUAGES


def get_language_keyboard():
    result = list()

    row = []
    for language in get_languages():
        row.append(f'{language[1]} ({language[0]})')
        if len(row) == 2:
            result.append(row)
            row = []

    if len(row):
        result.append(row)

    return result
