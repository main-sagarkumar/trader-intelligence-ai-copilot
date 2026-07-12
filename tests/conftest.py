"""Deterministic test environment independent of developer shell variables."""

import os


os.environ["DEBUG"] = "false"
