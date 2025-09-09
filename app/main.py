# main.py

import uvicorn
from config import config

def main():
    # uvicorn.run("app.app:app", host="localhost", port=config.PORT, reload=True)
    
  uvicorn.run("app.app:app", host="0.0.0.0", port=config.PORT, reload=False)

if __name__ == "__main__":
    main()