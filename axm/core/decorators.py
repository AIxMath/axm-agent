"""Decorators for defining agents and tools"""

import functools
import inspect
from typing import Any, Callable, Optional, Type, get_type_hints

from pydantic import BaseModel, create_model


def _create_pydantic_model(func: Callable) -> Type[BaseModel]:
    """Create a Pydantic model from function signature"""
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    fields: dict[str, Any] = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        annotation = hints.get(param_name, Any)
        default = ... if param.default == inspect.Parameter.empty else param.default

        fields[param_name] = (annotation, default)

    # Get the docstring and parse parameter descriptions
    docstring = inspect.getdoc(func) or ""

    model = create_model(
        f"{func.__name__}_model",
        __doc__=docstring,
        **fields,  # type: ignore[arg-type]
    )
    return model


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    """
    Decorator to mark a function as a tool that can be used by an agent.

    Example:
        @tool
        def get_weather(city: str) -> str:
            '''Get the weather for a city'''
            return f"Sunny in {city}"

        @tool(name="calculator", description="Performs calculations")
        def calc(expression: str) -> float:
            return eval(expression)
    """

    def decorator(f: Callable) -> Callable:
        # Store metadata on the function
        f._is_tool = True  # type: ignore
        f._tool_name = name or f.__name__  # type: ignore
        f._tool_description = description or inspect.getdoc(f) or f.__name__  # type: ignore
        f._tool_model = _create_pydantic_model(f)  # type: ignore

        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        # Copy metadata to wrapper
        wrapper._is_tool = True  # type: ignore
        wrapper._tool_name = f._tool_name  # type: ignore
        wrapper._tool_description = f._tool_description  # type: ignore
        wrapper._tool_model = f._tool_model  # type: ignore

        return wrapper

    if func is None:
        # Called with arguments: @tool(name="...")
        return decorator
    else:
        # Called without arguments: @tool
        return decorator(func)


def agent_method(func: Callable) -> Callable:
    """
    Decorator to mark a method as an agent-enhanced method.
    These methods can access the agent's LLM capabilities.

    Example:
        class MyAgent(Agent):
            @agent_method
            def analyze(self, text: str) -> str:
                return self.run(f"Analyze this text: {text}")
    """
    func._is_agent_method = True  # type: ignore
    return func


def validate_output(schema: Type[BaseModel]) -> Callable:
    """
    Decorator to validate function output against a Pydantic schema.

    Example:
        class Output(BaseModel):
            result: str
            confidence: float

        @validate_output(Output)
        def process(data: str) -> dict:
            return {"result": data, "confidence": 0.95}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> BaseModel:
            result = func(*args, **kwargs)
            if isinstance(result, dict):
                return schema(**result)
            elif isinstance(result, schema):
                return result
            else:
                raise ValueError(f"Output must be dict or {schema.__name__}")

        return wrapper

    return decorator


def retry(max_attempts: int = 3, exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to retry a function on failure.

    Example:
        @retry(max_attempts=3, exceptions=(ValueError, ConnectionError))
        def unstable_operation():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        continue
            raise last_exception  # type: ignore

        return wrapper

    return decorator
