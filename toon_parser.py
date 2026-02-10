"""
TOON (Token-Oriented Object Notation) Parser for Bit by Bit Game
Based on TOON Specification v3.0
"""

import re
from typing import Any, Dict, List, Union, Optional
from enum import Enum


class ToonParseError(Exception):
    """Custom exception for TOON parsing errors"""

    pass


class ToonNodeType(Enum):
    OBJECT = "object"
    ARRAY = "array"
    PRIMITIVE = "primitive"


class ToonNode:
    """Represents a node in the parsed TOON structure"""

    def __init__(self, node_type: ToonNodeType, value: Any, key: Optional[str] = None):
        self.type = node_type
        self.value = value
        self.key = key

    def __repr__(self):
        return f"ToonNode({self.type}, {self.value}, {self.key})"


class ToonParser:
    """TOON format parser with support for objects, arrays, and primitives"""

    def __init__(self, strict: bool = True):
        self.strict = strict
        self.lines: List[str] = []
        self.current_depth = 0
        self.root: Optional[ToonNode] = None

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse TOON content and return Python dictionary"""
        self.lines = [line.rstrip() for line in content.split("\n")]
        self.lines = [
            line for line in self.lines if line.strip() or not line.strip()
        ]  # Keep blank lines in non-strict mode

        # Determine root form
        if not self.lines or all(not line.strip() for line in self.lines):
            return {}

        # Check if first non-empty line is an array header
        first_content = next((line for line in self.lines if line.strip()), None)
        if first_content and self._is_array_header(first_content):
            # Root is array
            return self._parse_root_array()
        elif len([line for line in self.lines if line.strip() and ":" in line]) > 0:
            # Root is object
            return self._parse_root_object()
        else:
            # Root is primitive
            if first_content:
                return self._parse_primitive(first_content.strip())
            return {}

    def _is_array_header(self, line: str) -> bool:
        """Check if line is an array header"""
        stripped = line.strip()
        return stripped.startswith("[") and "]" in stripped and stripped.endswith(":")

    def _parse_root_array(self) -> List[Any]:
        """Parse root array"""
        first_line = next((line for line in self.lines if line.strip()), None)
        header_match = re.match(r"^\[([0-9]+)([|\t])?\]:(.*)$", first_line.strip())

        if not header_match:
            if self.strict:
                raise ToonParseError(f"Invalid array header: {first_line}")
            return []

        length = int(header_match.group(1))
        delimiter = header_match.group(2) if header_match.group(2) else ","

        if header_match.group(3):  # Inline values
            values_str = header_match.group(3).strip()
            if values_str:
                return self._split_inline_values(values_str, delimiter)

        # Parse as list items
        result = []
        in_array = True
        list_item_start = 1

        for line in self.lines[self.lines.index(first_line) + 1 :]:
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent < list_item_start:
                break  # End of array

            if line.strip().startswith("- "):
                # List item with value
                item_value = line.strip()[2:].strip()
                if item_value:
                    result.append(self._parse_primitive(item_value))
            elif line.strip() == "-":
                # Empty list item (object)
                result.append({})
            else:
                # Nested structure in list item
                # For simplicity, we'll handle basic cases
                pass

        if self.strict and len(result) != length:
            raise ToonParseError(
                f"Array length mismatch: declared {length}, got {len(result)}"
            )

        return result[:length]  # Ensure we don't exceed declared length

    def _parse_root_object(self) -> Dict[str, Any]:
        """Parse root object"""
        result = {}
        stack = [result]

        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            if not line.strip():
                i += 1
                continue

            indent = len(line) - len(line.lstrip())

            if ":" in line.strip():
                # Key-value pair
                key_part, value_part = line.split(":", 1)
                key = key_part.strip()
                value = value_part.strip()

                if value:
                    # Primitive value
                    parsed_value = self._parse_primitive(value)
                    stack[-1][key] = parsed_value
                else:
                    # Object or array as value
                    # Look ahead for nested content
                    i += 1
                    if i >= len(self.lines):
                        stack[-1][key] = {}
                        break

                    next_line = self.lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())

                    if next_indent > indent:
                        # Nested object
                        nested_obj = self._parse_nested_object(i, indent)
                        stack[-1][key] = nested_obj["data"]
                        i = nested_obj["next_index"]
                    elif next_line.strip().startswith("["):
                        # Array
                        nested_array = self._parse_nested_array(i, indent)
                        stack[-1][key] = nested_array["data"]
                        i = nested_array["next_index"]
                    else:
                        # Empty object
                        stack[-1][key] = {}

            i += 1

        return result

    def _parse_nested_object(
        self, start_index: int, parent_indent: int
    ) -> Dict[str, Any]:
        """Parse nested object starting at start_index"""
        result = {}
        i = start_index

        while i < len(self.lines):
            line = self.lines[i]
            if not line.strip():
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())

            if current_indent <= parent_indent:
                break

            if ":" in line.strip():
                key_part, value_part = line.split(":", 1)
                key = key_part.strip()
                value = value_part.strip()

                if value:
                    result[key] = self._parse_primitive(value)
                else:
                    # Nested object or array
                    i += 1
                    if i < len(self.lines):
                        next_line = self.lines[i]
                        next_indent = len(next_line) - len(next_line.lstrip())

                        if next_indent > current_indent:
                            if next_line.strip().startswith("["):
                                # Nested array
                                nested = self._parse_nested_array(i, current_indent)
                                result[key] = nested["data"]
                                i = nested["next_index"]
                            else:
                                # Nested object
                                nested = self._parse_nested_object(i, current_indent)
                                result[key] = nested["data"]
                                i = nested["next_index"]
                        else:
                            result[key] = {}

            i += 1

        return {"data": result, "next_index": i}

    def _parse_nested_array(
        self, start_index: int, parent_indent: int
    ) -> Dict[str, Any]:
        """Parse nested array starting at start_index"""
        first_line = self.lines[start_index]
        header_match = re.match(r"^\[([0-9]+)([|\t])?\]:(.*)$", first_line.strip())

        if not header_match:
            if self.strict:
                raise ToonParseError(f"Invalid array header: {first_line}")
            return {"data": [], "next_index": start_index + 1}

        length = int(header_match.group(1))
        delimiter = header_match.group(2) if header_match.group(2) else ","

        if header_match.group(3):  # Inline values
            values_str = header_match.group(3).strip()
            values = (
                self._split_inline_values(values_str, delimiter) if values_str else []
            )
            return {"data": values[:length], "next_index": start_index + 1}

        # Parse as list items
        result = []
        i = start_index + 1

        while i < len(self.lines):
            line = self.lines[i]
            if not line.strip():
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= parent_indent:
                break

            if line.strip().startswith("- "):
                item_value = line.strip()[2:].strip()
                if item_value:
                    result.append(self._parse_primitive(item_value))
                else:
                    result.append({})
            i += 1

        if self.strict and len(result) != length:
            raise ToonParseError(
                f"Array length mismatch: declared {length}, got {len(result)}"
            )

        return {"data": result[:length], "next_index": i}

    def _split_inline_values(self, values_str: str, delimiter: str) -> List[Any]:
        """Split inline array values by delimiter"""
        if not values_str:
            return []

        values = []
        current = ""
        in_quotes = False
        escape_next = False

        for char in values_str:
            if escape_next:
                current += char
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                current += char
            elif char == '"' and not escape_next:
                in_quotes = not in_quotes
                current += char
            elif char == delimiter and not in_quotes:
                values.append(self._parse_primitive(current.strip()))
                current = ""
            else:
                current += char

        if current.strip():
            values.append(self._parse_primitive(current.strip()))

        return values

    def _parse_primitive(self, token: str) -> Any:
        """Parse a primitive value (string, number, boolean, null)"""
        token = token.strip()

        if not token:
            return ""

        # Handle quoted strings
        if token.startswith('"') and token.endswith('"'):
            return self._unescape_string(token[1:-1])

        # Handle boolean and null
        if token == "true":
            return True
        elif token == "false":
            return False
        elif token == "null":
            return None

        # Handle numbers
        try:
            # Try integer first
            if re.match(r"^-?\d+$", token):
                return int(token)
            # Try float
            if re.match(r"^-?\d*\.\d+$", token):
                return float(token)
            # Try scientific notation
            if re.match(r"^-?\d+(?:\.\d+)?[eE][+-]?\d+$", token):
                return float(token)
        except ValueError:
            pass

        # Default to string
        return token

    def _unescape_string(self, s: str) -> str:
        """Unescape TOON string"""
        result = ""
        escape_next = False

        for char in s:
            if escape_next:
                result += char
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
            elif char == "n" and escape_next:
                result += "\n"
                escape_next = False
            elif char == "r" and escape_next:
                result += "\r"
                escape_next = False
            elif char == "t" and escape_next:
                result += "\t"
                escape_next = False
            elif char == '"' and escape_next:
                result += '"'
                escape_next = False
            else:
                result += char
                if escape_next:
                    escape_next = False

        return result


def load_toon_file(filepath: str, strict: bool = True) -> Dict[str, Any]:
    """Load and parse a TOON file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        parser = ToonParser(strict)
        return parser.parse(content)
    except FileNotFoundError:
        raise ToonParseError(f"File not found: {filepath}")
    except UnicodeDecodeError as e:
        raise ToonParseError(f"Unicode decode error in {filepath}: {e}")


def save_toon_file(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """Save data as TOON file (simplified encoder)"""
    lines = []

    def _format_primitive(value: Any) -> str:
        """Format primitive value for TOON output"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Check if quoting is needed
            if (
                any(
                    c in value
                    for c in [":", '"', "\\", "\n", "\r", "\t", "[", "]", "{", "}"]
                )
                or value.strip() != value
            ):
                # Need to escape and quote
                escaped = (
                    value.replace("\\", "\\\\")
                    .replace('"', '\\"')
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t")
                )
                return f'"{escaped}"'
            return value
        else:
            return str(value)

    def _format_key(key: str) -> str:
        """Format key for TOON output"""
        if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", key):
            return key
        else:
            # Need to quote the key
            escaped = key.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{_format_key(key)}:")
            for subkey, subvalue in value.items():
                subindent = " " * (indent + 2)
                if isinstance(subvalue, dict):
                    lines.append(f"{subindent}{_format_key(subkey)}:")
                    for subsubkey, subsubvalue in subvalue.items():
                        subsubindent = " " * (indent + 4)
                        lines.append(
                            f"{subsubindent}{_format_key(subsubkey)}: {_format_primitive(subsubvalue)}"
                        )
                elif isinstance(subvalue, list):
                    # Simple array representation
                    if subvalue:
                        subindent = " " * (indent + 2)
                        values = ",".join(_format_primitive(v) for v in subvalue)
                        lines.append(
                            f"{subindent}{_format_key(subkey)}[{len(subvalue)}]: {values}"
                        )
                    else:
                        subindent = " " * (indent + 2)
                        lines.append(f"{subindent}{_format_key(subkey)}[0]:")
                else:
                    subindent = " " * (indent + 2)
                    lines.append(
                        f"{subindent}{_format_key(subkey)}: {_format_primitive(subvalue)}"
                    )
        elif isinstance(value, list):
            # Root array
            if value:
                values = ",".join(_format_primitive(v) for v in value)
                lines.append(f"[{len(value)}]: {values}")
            else:
                lines.append(f"[0]:")
        else:
            lines.append(f"{_format_key(key)}: {_format_primitive(value)}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
