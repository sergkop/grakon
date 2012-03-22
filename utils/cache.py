from django.core.cache import cache

from datetime import datetime

def cache_view(key_generator, timeout, only_anonym=True):
    """ key_generator = lambda args, kwargs: key """
    def decorator(func):
        def new_func(request, *args, **kwargs):
            t4 = datetime.now()
            if (only_anonym and not request.user.is_authenticated()) or not only_anonym:
                key = key_generator(args, kwargs)

                res = cache.get(key)
                if res:
                    return res

                t1 = datetime.now()
                res = func(request, *args, **kwargs)
                cache.set(key, res, timeout)
            else:
                res = func(request, *args, **kwargs)

            return res

        return new_func

    return decorator
