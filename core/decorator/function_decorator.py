from functools import wraps

def markus_function(function):
    function._callable = True
    @wraps(function)
    def wrapper(*args, **kwargs):
        function_result = function(*args, **kwargs)
        return function_result
    return wrapper