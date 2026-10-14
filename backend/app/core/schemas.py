"""
Shared Pydantic base model enforcing the camelCase JSON field-naming
convention chosen in API Specification v1.0 Section 6 ("Proposed: camelCase
for all JSON field names ... idiomatic convention for a TypeScript/
JavaScript frontend").

Python-side field names remain snake_case (idiomatic Python); this base
class handles the snake_case <-> camelCase translation at the API
boundary automatically.
"""

from pydantic import BaseModel, ConfigDict


def to_camel(snake_str: str) -> str:
    """Convert a snake_case string to camelCase (e.g. `is_active` -> `isActive`)."""
    first, *rest = snake_str.split("_")
    return first + "".join(word.capitalize() for word in rest)


class CamelModel(BaseModel):
    """
    Base class for all request/response schemas. Accepts and emits
    camelCase JSON field names while keeping snake_case Python
    attribute names internally.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
