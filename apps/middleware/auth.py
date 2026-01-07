from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SlidingTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if hasattr(request.state, "new_access_token"):
            response.headers["X-New-Access-Token"] = request.state.new_access_token

        return response
