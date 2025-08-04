"""
Singleton metaclass for creating singleton instances
"""

class SingletonMeta(type):
    """
    Metaclass that creates singleton instances.
    
    Usage:
        class MyService(metaclass=SingletonMeta):
            def __init__(self):
                # initialization code
                pass
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls] 