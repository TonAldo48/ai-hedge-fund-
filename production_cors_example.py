# Example: Production CORS configuration for custom domain
from fastapi.middleware.cors import CORSMiddleware

# Production CORS settings with custom domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://api.yourdomain.com",
        "https://docs.yourdomain.com",
        # Add your frontend domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# For development, you can still allow localhost:
# allow_origins=["https://yourdomain.com", "http://localhost:3000"] 