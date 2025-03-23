"""Main"""

import uvicorn
from api import create_app

app = create_app()


def main():
    """Run the application."""
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    main()
