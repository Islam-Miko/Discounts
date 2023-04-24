from functools import wraps

from django.http import HttpRequest

from .tasks import increment_count
from .utils import get_id_from_path


def increment_views(view_func):
    """
    Decorator to start discounts view incrementing
    task.
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        path_url = request.get_raw_uri()
        id_ = get_id_from_path(path_url)
        increment_count(id_)
        return view_func(request, *args, **kwargs)

    return wrapper
