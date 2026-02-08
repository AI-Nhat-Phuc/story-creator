from interfaces.api_backend import APIBackend

api = APIBackend()
app = api.app  # Expose Flask app for Vercel/WSGI/ASGI
