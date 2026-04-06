"""
main.py — Application entry point.

Start with:
    uvicorn main:app --reload         (development)
    python main.py                    (also works)
"""

import uvicorn
from app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
    )
