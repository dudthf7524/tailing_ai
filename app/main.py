# main.py

import uvicorn
from config import config

def main():
    # uvicorn.run("app.app:app", host="localhost", port=config.PORT, reload=True)
    
  uvicorn.run("app.app:app", host="175.106.99.173", port=config.PORT, reload=False)

if __name__ == "__main__":
    main()