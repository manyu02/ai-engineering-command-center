import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start

            logging.info(
                "%s %s -> %s | %.3fs",
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )

            return response

        except Exception:
            duration = time.perf_counter() - start

            logging.exception(
                "%s %s failed | %.3fs",
                request.method,
                request.url.path,
                duration,
            )

            raise
