import pkgutil
import importlib

__all__ = []

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    print(f"Loading module: {module_name}")
    module = importlib.import_module(f"{__name__}.{module_name}")
    for attr in dir(module):
        print(f"  Found attribute: {attr}")
        obj = getattr(module, attr)
        if isinstance(obj, type):  # is a class
            print(f"     Adding class: {attr}")
            globals()[attr] = obj
            __all__.append(attr)