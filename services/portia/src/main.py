import os
import uvicorn
from dotenv import load_dotenv

def main():
    load_dotenv()
    port = int(os.getenv("PORT","8000"))
    uvicorn.run("src.portia_app:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()
