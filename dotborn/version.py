def get_version():
    try:
        with open('VERSION.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"