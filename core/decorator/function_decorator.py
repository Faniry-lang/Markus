from functools import wraps

def markus_function(needs_validation: bool = False):
    def decorator(function):
        function._callable = True
        function._needs_validation = needs_validation
        @wraps(function)
        def wrapper(*args, **kwargs):
            function_result = function(*args, **kwargs)
            return function_result
        return wrapper
    return decorator