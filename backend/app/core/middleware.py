"""
Middleware for rate limiting and security headers.
"""
from fastapi import Request
from slowapi import Limiter
from starlette.types import ASGIApp, Receive, Scope, Send


def get_real_ip(request: Request) -> str:
    """
    Get the real IP address from the request.

    Handles both direct connections and connections through proxies.
    Whitelists localhost/127.0.0.1 for testing.
    """
    # Check for X-Forwarded-For header (proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip = forwarded.split(",")[0].strip()
    else:
        # Direct connection
        ip = request.client.host if request.client else "unknown"

    return ip


# Create limiter instance
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=[],  # No default limits, we'll set them per endpoint
    storage_uri="memory://",  # Use in-memory storage
)


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.

    Adds the following headers:
    - X-Frame-Options: DENY (prevent clickjacking)
    - X-Content-Type-Options: nosniff (prevent MIME type sniffing)
    - X-XSS-Protection: 1; mode=block (enable XSS filtering)
    - Referrer-Policy: strict-origin-when-cross-origin (control referrer info)
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware with app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process request and add security headers to response."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            """Add security headers to response."""
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-frame-options", b"DENY"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                ])
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)
