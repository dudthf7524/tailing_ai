# main.py

import uvicorn
from config import config

def main():
    uvicorn.run("app.app:app", host="localhost", port=config.PORT, reload=True)
    


if __name__ == "__main__":
    main()