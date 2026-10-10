from pydantic import BaseModel, ValidationError


def validate_json_schema(data: dict, model: type[BaseModel]) -> bool:
    try:
        model.model_validate(data)
        return True
    except ValidationError:
        return False
