#!/usr/bin/env python3
"""Compatibility entry point for the modular print pipeline.

The previous ReportLab vector-scene prototype is intentionally retired.
No placeholder artwork is generated. Supply all 24 original illustrations
under assets/artwork/ before creating a print-ready PDF.
"""
from book.render import main

if __name__ == "__main__":
    main()
