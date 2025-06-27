"""
    Script to import data from .json files
    To execute this script run:
        1) python manage.py shell
        2) from cards.filling import filling_all
        3) filling_all()
        4) exit()
"""

from .filling import filling_all, filling_enumerate


__all__ = [
    filling_all,
    filling_enumerate]
