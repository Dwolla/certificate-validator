# -*- coding: utf-8 -*-
"""
Shared Logger Module.

Placing it here to allow unified logging controls across modules
"""

import logging

logger = logging.getLogger('certificate_validator')
logger.setLevel(logging.DEBUG)
