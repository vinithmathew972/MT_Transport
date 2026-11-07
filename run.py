import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"\n==========================================================")
    print(f" Mother Theresa Transport Management System")
    print(f" Safe Journey... Stronger Tomorrow...")
    print(f" Server running at: http://{host}:{port}")
    print(f" - Home Page:      http://{host}:{port}/")
    print(f" - Owner Login:    http://{host}:{port}/login")
    print(f" - Dashboard:      http://{host}:{port}/dashboard")
    print(f" - API Docs:       http://{host}:{port}/docs")
    print(f"==========================================================\n")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
