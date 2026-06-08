import random
import string

BASE62_CHARS = string.ascii_letters + string.digits


def generate_random_code(length: int = 6) -> str:
    return "".join(random.choices(BASE62_CHARS, k=length))


def generate_unique_code(length: int = 6, max_attempts: int = 10) -> str:
    from .models import URL

    for _ in range(max_attempts):
        code = generate_random_code(length)
        if not URL.objects.filter(short_code=code).exists():
            return code

        raise RuntimeError(
            f"could not generate a unique short code in {max_attempts} attempts"
        )


def get_client_ip(request) -> str | None:
    x_forwarded_for = request.META.get("HTTP_X_FORWARED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
