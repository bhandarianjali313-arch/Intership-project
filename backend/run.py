from __future__ import annotations

import os
import sys
from pathlib import Path


# ============================================================================
# PROJECT PATH SETUP
# ============================================================================

BACKEND_DIR = Path(
    __file__
).resolve().parent

PROJECT_ROOT = (
    BACKEND_DIR.parent
)


# Allow imports from:
#
#   backend/app/
#
# and:
#
#   ml/
#
for path in (
    PROJECT_ROOT,
    BACKEND_DIR,
):
    path_string = str(path)

    if path_string not in sys.path:
        sys.path.insert(
            0,
            path_string,
        )


# Uvicorn uses a separate process when reload=True.
# PYTHONPATH is therefore also updated so that the
# spawned process can import both app and ml modules.

existing_pythonpath = (
    os.environ.get(
        "PYTHONPATH",
        "",
    )
)

python_paths = [
    str(PROJECT_ROOT),
    str(BACKEND_DIR),
]

if existing_pythonpath:
    python_paths.append(
        existing_pythonpath
    )

os.environ[
    "PYTHONPATH"
] = os.pathsep.join(
    python_paths
)


# Imports must happen after path setup.
import uvicorn

from app.config import (
    HOST,
    PORT,
)


# ============================================================================
# START SERVER
# ============================================================================

if __name__ == "__main__":

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )