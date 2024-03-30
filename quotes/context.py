from urllib.parse import urlparse


def base_context_processor(request):
    base_url = request.build_absolute_uri("/").rstrip("/")
    url = urlparse(base_url)
    return {
        'BASE_URL': base_url,
        "HOST": base_url.replace(url.scheme + "://", "")
    }
