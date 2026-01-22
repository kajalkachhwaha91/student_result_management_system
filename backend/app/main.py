
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import student_routes, role_routes, user_routes, auth_routes,marks_upload, assignment, bonafiled 
from backend.app.routes import chatbot_routes



app = FastAPI()

app.include_router(student_routes.router)
app.include_router(role_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(marks_upload.router)
app.include_router(bonafiled.router) 
app.include_router(assignment.router)
app.include_router(chatbot_routes.router)

# CORS setup (so React frontend can access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(student_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to SRMS API"}
