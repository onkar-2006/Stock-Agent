from endpoint import app
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",    
    "http://localhost:5173",   
    "http://127.0.0.1:8000",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,        
    allow_methods=["*"],              
    allow_headers=["*"],              
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

