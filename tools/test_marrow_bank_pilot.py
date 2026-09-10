#!/usr/bin/env python3
"""Expanded Marrow bank regression wrapper for the approved UI branch."""
from __future__ import annotations

import sys

# The Engineering Gate invokes this test with --data-only before the generated
# app has been built. The full build invokes it after apply_marrow_bank_pilot.py;
# only that path needs the runtime MARROW_DATA overlay.
if "--data-only" not in sys.argv:
    from apply_marrow_source_expansion_overlay import main as apply_source_expansion

    apply_source_expansion()

from test_marrow_bank_pilot_expanded_core import main

if __name__ == "__main__":
    main()
