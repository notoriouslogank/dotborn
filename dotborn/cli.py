import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Dotborn system configuration management tool.")

    parser.add_argument("--run", choices=["backup", "install", "migrate"], help="Which utility to run")
    parser.add_argument("--compress", action="store_true", help="Whether or not to compress backup")
    parser.add_argument("--dry-run", action="store_true", help="Preview ations without performing them")

    return parser.parse_args()