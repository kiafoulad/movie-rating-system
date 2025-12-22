from fastapi import FastAPI

from app.controllers.movies import router as movies_router

# Create FastAPI application instance
app = FastAPI(
    title="Movie Rating System API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    """
    Simple health check endpoint to verify that the API server is running.
    """
    return {
        "status": "ok",
        "message": "Movie Rating System API is running.",
    }


# Include routers for different resource groups
app.include_router(movies_router)
