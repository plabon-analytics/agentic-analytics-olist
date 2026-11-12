import random
import time

RETRY_CODES = {429, 500, 502, 503, 504}


def is_transient(error):
    if isinstance(error, ValueError):
        return True
    if isinstance(error, TimeoutError):
        return True
    return getattr(error, "code", None) in RETRY_CODES


def call_with_retry(make_call, is_transient, max_attempts=4, base_wait=1.0):
    for attempt in range(1, max_attempts + 1):
        try:
            data = make_call()
            return {"ok": True, "data": data, "attempts": attempt}
        except Exception as error:
            if not is_transient(error):
                return {
                    "ok": False,
                    "error_type": "permanent",
                    "detail": str(error),
                    "attempts": attempt,
                }
            if attempt == max_attempts:
                return {
                    "ok": False,
                    "error_type": "gave_up",
                    "detail": str(error),
                    "attempts": attempt,
                }
            wait = base_wait * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            print(f"  attempt {attempt} failed ({error}). Waiting {wait:.1f} seconds.")
            time.sleep(wait)