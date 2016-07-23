import functools


class memoize(object):
    def __init__(self, func):
        self.func = func
        self.cache = dict()
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        key = (str(args), str(kwargs))

        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)
        return self.cache[key]


class memoize_with(object):
    def __init__(self, hash_function):
        self.hash_function = hash_function
        self.cache = dict()

    def __call__(self, func):
        parent = self

        def memoized(*args, **kwargs):
            if kwargs == {}:
                key = parent.hash_function(*args)
            else:
                key = parent.hash_function(*args, **kwargs)

            if key not in self.cache:
                self.cache[key] = func(*args, **kwargs)
            return self.cache[key]

        return memoized
