#!/usr/bin/env python3
"""Expanded Marrow bank regression wrapper for the approved UI branch."""
from apply_marrow_source_expansion_overlay import main as apply_source_expansion

apply_source_expansion()

from test_marrow_bank_pilot_expanded_core import main

if __name__ == "__main__":
    main()
