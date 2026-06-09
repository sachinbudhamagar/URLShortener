import random
import string

BASE62_CHARS = string.ascii_letters + string.digits


def generate_unique_code(length: int = 6, max_attempts: int = 10) -> str:
    from .models import URL

    for _ in range(max_attempts):
        code = string.ascii_letters + string.digits
        code = "".join(random.choices(BASE62_CHARS, k=length))
        if not URL.objects.filter(short_code=code).exists():
            return code
    raise RuntimeError(
        f"could not generate a unique short code in {max_attempts} attempts"
    )


def get_client_ip(request) -> str | None:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
