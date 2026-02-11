import inspect
import pkgutil
import importlib
from pydantic import BaseModel
from typing import Dict, Any, List
import core.functions

class MarkusTool(BaseModel):
    name: str
    doc: str
    parameters: Dict[str, str]
    return_type: str

tools_registry: Dict[str, Any] = {}

def get_tools(package) -> List[MarkusTool]:

    tools: List[MarkusTool] = []

    for finder, modname, ispkg in pkgutil.iter_modules(package.__path__):
        full_modname = f"{package.__name__}.{modname}"
        module = importlib.import_module(full_modname)

        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and getattr(obj, "_callable", False):
                sig = inspect.signature(obj)
                params: Dict[str, str] = {}
                for param_name, param in sig.parameters.items():
                    if param.annotation != inspect.Parameter.empty:
                        if isinstance(param.annotation, type):
                            params[param_name] = param.annotation.__name__
                        else:
                            params[param_name] = str(param.annotation)
                    else:
                        params[param_name] = "Any"

                if sig.return_annotation != inspect.Signature.empty:
                    return_type = sig.return_annotation.__name__ if isinstance(sig.return_annotation, type) else str(sig.return_annotation)
                else:
                    return_type = "Any"

                tool = MarkusTool(
                    name=obj.__name__,
                    doc=obj.__doc__ or "",
                    parameters=params,
                    return_type=return_type
                )
                tools.append(tool)

                tools_registry[obj.__name__] = obj

        if ispkg:
            tools.extend(get_tools(module))

    return tools

def get_markus_tools() -> List[MarkusTool]:
    return get_tools(core.functions)
