# import sys, os
# print("CURRENT FILE:", __file__)
# print("WORKING DIR:", os.getcwd())
# print("PYTHONPATH:", sys.path)
from fastapi import FastAPI
from backend.app.routes import student_routes
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import student_routes, role_routes, user_routes, auth_routes,marks_upload, assignment



app = FastAPI()

app.include_router(student_routes.router)
app.include_router(role_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(marks_upload.router)
app.include_router(assignment.router)

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
