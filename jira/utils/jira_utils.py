from datetime import datetime, timedelta
from typing import Dict, Any, Callable
from typing import Tuple

class JiraUtils:
    """This class provides various utility methods to process data from Jira and prepare it for ingestion."""
    @staticmethod
    def add_fields_from_record(*fields_path: Tuple[str, str]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        This function returns an inner function that splits each field_path by dots to handle nested fields.
        It traverses the dictionary to extract the value of the nested field and adds it to the record with a specified name.

        >>Example:
        >>record = {
        "fields": {
            "updated": "2024-02-23T15:05:39.155+1100",
            "created": "2024-02-22T10:00:00.000+1100",
            "details": {
                "metadata": {
                    "created_by": "user1"
                }
            }
        }
    }
        >> To output a function that adds nested fields, `updated`, `created`, and `details.metadata.created_by` to the record with specified names, pass the arguments as follows:
        >> add_fields_from_record(("fields.updated", "updated"), ("fields.created", "created"), ("fields.details.metadata.created_by", "created_by"))

        Args:
            *fields_path (Tuple[str, str]): Tuples where the first element is the path to the nested field in the record, separated by dot notation, and the second element is the name of the new field to be added.
        Returns:
            Callable[[Dict[str, Any]], Dict[str, Any]]: The function that traverses the dictionary to extract the value of the nested field and adds it to the record with the specified name.
        """
        def inner(record: Dict[str, Any]) -> Dict[str, Any]:
            def get_nested_value(d: Any, keys: list) -> Any:
                for key in keys:
                    if isinstance(d, dict):
                        d = d.get(key)
                    elif isinstance(d, list):
                        try:
                            key = int(key)
                            d = d[key]
                        except (ValueError, IndexError) as e:
                            raise KeyError(f"Invalid list index '{key}' in path.") from e
                    else:
                        raise KeyError(f"Invalid path segment '{key}' in path.")
                return d

            for field_path, new_field_name in fields_path:
                if not isinstance(field_path, str) or not field_path:
                    raise TypeError(f"Invalid field path argument: '{field_path}'. It must be a non-empty string.")

                keys = field_path.split('.')
                try:
                    value = get_nested_value(record, keys)
                    record[new_field_name] = value
                except KeyError as e:
                    raise KeyError(f"The nested field '{field_path}' is not present in the record:`{record}`") from e
                except TypeError as e:
                    raise TypeError(f"The field path '{field_path}' is invalid in the record: `{record}`") from e
            return record
        return inner
    
    @staticmethod
    def remove_fields_from_record(*fields: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        This function returns an inner function that removes specified fields from a given record.

        Args:
            *fields (str)): Fields to be removed.

        Returns:
            Callable[[Dict[str, Any]], Dict[str, Any]]: The function that returns the updated record with the specified fields removed.

        Notes:
            If a specified field is not present in the record, a warning message will be printed.
        """
        def inner(record: Dict[str, Any]) -> Dict[str, Any]:
            for field in fields:
                if field in record:
                    del record[field]
                else:
                    print(f"Warning: The field '{field}' is not present in the record: `{record}`")
            return record
        return inner
    @staticmethod
    def add_partition_date(partition_date: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        This function adds a partition date to a given record.

        Args:
            partition_date (str): The partition date string in the format 'YYYY-MM-DD'.

        Returns:
            Callable[[Dict[str, Any]], Dict[str, Any]]: The function that returns the updated record with the partition date added.

        Raises:
            ValueError: If the partition date is not in the correct format (YYYY-MM-DD).
        """
        def inner(record):
            try:
                datetime.strptime(partition_date, '%Y-%m-%d')
                record["partition_date"] = partition_date
            except ValueError as e:
                raise ValueError("Incorrect data format, should be YYYY-MM-DD") from e
            return record
        return inner
    @staticmethod
    def get_prev_date(date_string: str) -> str:
        """
        Get the date one day earlier than the given date string.

        Args:
            date_string (str): The input date string in the format '%Y-%m-%d'.

        Returns:
            str: The date string one day earlier than the input date string, in the format '%Y-%m-%d'.

        Raises:
            ValueError: If the input date string is not in the format '%Y-%m-%d'.

        Examples:
            >>> get_date_one_day_earlier('2022-01-01')
            '2021-12-31'
        """
        date_string_dt = datetime.strptime(date_string, '%Y-%m-%d')
        data_date_dt = date_string_dt - timedelta(days=1)
        return data_date_dt.strftime('%Y-%m-%d')