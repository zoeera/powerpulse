import json
from datetime import date, datetime

try:
    from pydantic import BaseModel, Field, EmailStr
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    
    class Field:
        def __init__(self, default=..., **kwargs):
            self.default = default
            self.kwargs = kwargs

    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
                
        def model_dump(self) -> dict:
            res = {}
            for k, v in self.__dict__.items():
                if isinstance(v, (date, datetime)):
                    res[k] = v.isoformat()
                elif isinstance(v, BaseModel):
                    res[k] = v.model_dump()
                elif isinstance(v, list):
                    res[k] = [i.model_dump() if isinstance(i, BaseModel) else i for i in v]
                else:
                    res[k] = v
            return res

        def model_dump_json(self, indent: int = 2) -> str:
            return json.dumps(self.model_dump(), indent=indent, default=str)

        @classmethod
        def model_validate(cls, obj):
            if isinstance(obj, dict):
                return cls(**obj)
            return obj

    class EmailStr(str):
        pass

