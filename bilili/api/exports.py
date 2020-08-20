exports = {}


def export_api(route: str):
    def new_func(func):
        exports[route] = func
        return func

    return new_func
