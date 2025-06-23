from types import SimpleNamespace

class SafeNamespace(SimpleNamespace):
    def __init__(self, **kwargs):
        # Recursively convert dicts and lists to SafeNamespace
        for k, v in kwargs.items():
            if isinstance(v, dict):
                kwargs[k] = SafeNamespace(**v)
            elif isinstance(v, list):
                kwargs[k] = [
                    SafeNamespace(**i) if isinstance(i, dict) else i for i in v
                ]
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        # Override __getattr__ to return None for undefined attributes
        return None

    def __getitem__(self, name):
        # Implement __getitem__ to allow [] notation
        return getattr(self, name, None)

def main():
    data = {
        "a": 1,
        "b": {"c": 2, "d": {"e": 3}},
        "f": [{"g": 4}, {"h": 5}],
        "i": [1, 2, 3]
    }

    ns = SafeNamespace(**data)

    print("a:", ns.a)
    print("b.c:", ns.b.c)
    print("b.d.e:", ns.b.d.e)
    print("f[0].g:", ns.f[0].g)
    print("f[1].h:", ns.f[1].h)
    print("i:", ns.i)
    print("missing attribute (should be None):", ns.not_there)
    print("getitem access (should be None):", ns["not_there"])
    print("getitem nested:", ns["b"].d.e)

if __name__ == "__main__":
    main()