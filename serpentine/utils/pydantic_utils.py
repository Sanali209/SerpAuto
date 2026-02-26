try:
    from pydantic import BaseModel, ConfigDict, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

    class FieldInfo:
        def __init__(self, default, default_factory):
            self.default = default
            self.default_factory = default_factory

    def Field(default=..., default_factory=None, **kwargs):
        return FieldInfo(default, default_factory)

    class BaseModel:
        def __init__(self, **kwargs):
            # Inspect class attributes and type hints (if available)
            cls = self.__class__

            # Get all annotated fields
            annotations = getattr(cls, "__annotations__", {})

            for name in annotations:
                # Check if passed in kwargs
                if name in kwargs:
                    setattr(self, name, kwargs[name])
                    continue

                # Check for default value on class
                if hasattr(cls, name):
                    val = getattr(cls, name)
                    if isinstance(val, FieldInfo):
                        if val.default is not ...:
                            setattr(self, name, val.default)
                        elif val.default_factory:
                            setattr(self, name, val.default_factory())
                        else:
                            # Required field missing? Or default None?
                            setattr(self, name, None)
                    else:
                        # Simple default value
                        setattr(self, name, val)
                else:
                    # Required field missing
                    # In real Pydantic this raises error. Here we set None or ignore.
                    setattr(self, name, None)

        def model_dump(self, **kwargs):
            data = {}
            for k, v in self.__dict__.items():
                if k.startswith("_"):
                    continue
                if isinstance(v, BaseModel):
                    data[k] = v.model_dump(**kwargs)
                elif isinstance(v, list):
                    data[k] = [i.model_dump(**kwargs) if isinstance(i, BaseModel) else i for i in v]
                elif isinstance(v, dict):
                    data[k] = {dk: dv.model_dump(**kwargs) if isinstance(dv, BaseModel) else dv for dk, dv in v.items()}
                else:
                    data[k] = v
            return data

        def model_copy(self, deep=False):
            """Simplified model_copy for fallback implementation."""
            import copy
            if deep:
                return copy.deepcopy(self)
            return copy.copy(self)

        @classmethod
        def model_validate(cls, obj):
            if isinstance(obj, dict):
                return cls(**obj)
            raise ValueError("model_validate expects a dictionary")

        class Config:
            pass

    def ConfigDict(**kwargs):
        return kwargs
