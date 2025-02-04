"""This section describes unitxt operators for tabular data.

These operators are specialized in handling tabular data.
Input table format is assumed as:
{
  "header": ["col1", "col2"],
  "rows": [["row11", "row12"], ["row21", "row22"], ["row31", "row32"]]
}

------------------------
"""
import random
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from .dict_utils import dict_get
from .operators import FieldOperator, StreamInstanceOperator


class SerializeTable(ABC, FieldOperator):
    """TableSerializer converts a given table into a flat sequence with special symbols.

    Output format varies depending on the chosen serializer. This abstract class defines structure of a typical table serializer that any concrete implementation should follow.
    """

    # main method to serialize a table
    @abstractmethod
    def serialize_table(self, table_content: Dict) -> str:
        pass

    # method to process table header
    @abstractmethod
    def process_header(self, header: List):
        pass

    # method to process a table row
    @abstractmethod
    def process_row(self, row: List, row_index: int):
        pass


# Concrete classes implementing table serializers
class SerializeTableAsIndexedRowMajor(SerializeTable):
    """Indexed Row Major Table Serializer.

    Commonly used row major serialization format.
    Format:  col : col1 | col2 | col 3 row 1 : val1 | val2 | val3 | val4 row 2 : val1 | ...
    """

    def process_value(self, table: Any) -> Any:
        table_input = deepcopy(table)
        return self.serialize_table(table_content=table_input)

    # main method that processes a table
    # table_content must be in the presribed input format
    def serialize_table(self, table_content: Dict) -> str:
        # Extract headers and rows from the dictionary
        header = table_content.get("header", [])
        rows = table_content.get("rows", [])

        assert header and rows, "Incorrect input table format"

        # Process table header first
        serialized_tbl_str = self.process_header(header) + " "

        # Process rows sequentially starting from row 1
        for i, row in enumerate(rows, start=1):
            serialized_tbl_str += self.process_row(row, row_index=i) + " "

        # return serialized table as a string
        return serialized_tbl_str.strip()

    # serialize header into a string containing the list of column names separated by '|' symbol
    def process_header(self, header: List):
        return "col : " + " | ".join(header)

    # serialize a table row into a string containing the list of cell values separated by '|'
    def process_row(self, row: List, row_index: int):
        serialized_row_str = ""
        row_cell_values = [
            str(value) if isinstance(value, (int, float)) else value for value in row
        ]

        serialized_row_str += " | ".join(row_cell_values)

        return f"row {row_index} : {serialized_row_str}"


class SerializeTableAsMarkdown(SerializeTable):
    """Markdown Table Serializer.

    Markdown table format is used in GitHub code primarily.
    Format:
    |col1|col2|col3|
    |---|---|---|
    |A|4|1|
    |I|2|1|
    ...
    """

    def process_value(self, table: Any) -> Any:
        table_input = deepcopy(table)
        return self.serialize_table(table_content=table_input)

    # main method that serializes a table.
    # table_content must be in the presribed input format.
    def serialize_table(self, table_content: Dict) -> str:
        # Extract headers and rows from the dictionary
        header = table_content.get("header", [])
        rows = table_content.get("rows", [])

        assert header and rows, "Incorrect input table format"

        # Process table header first
        serialized_tbl_str = self.process_header(header)

        # Process rows sequentially starting from row 1
        for i, row in enumerate(rows, start=1):
            serialized_tbl_str += self.process_row(row, row_index=i)

        # return serialized table as a string
        return serialized_tbl_str.strip()

    # serialize header into a string containing the list of column names
    def process_header(self, header: List):
        header_str = "|{}|\n".format("|".join(header))
        header_str += "|{}|\n".format("|".join(["---"] * len(header)))
        return header_str

    # serialize a table row into a string containing the list of cell values
    def process_row(self, row: List, row_index: int):
        row_str = ""
        row_str += "|{}|\n".format("|".join(str(cell) for cell in row))
        return row_str


# truncate cell value to maximum allowed length
def truncate_cell(cell_value, max_len):
    if cell_value is None:
        return None

    if isinstance(cell_value, int) or isinstance(cell_value, float):
        return None

    if cell_value.strip() == "":
        return None

    if len(cell_value) > max_len:
        return cell_value[:max_len]

    return None


class TruncateTableCells(StreamInstanceOperator):
    """Limit the maximum length of cell values in a table to reduce the overall length.

    Args:
        max_length (int) - maximum allowed length of cell values
        For tasks that produce a cell value as answer, truncating a cell value should be replicated
        with truncating the corresponding answer as well. This has been addressed in the implementation.

    """

    max_length: int = 15
    table: str = None
    text_output: Optional[str] = None
    use_query: bool = False

    def process(
        self, instance: Dict[str, Any], stream_name: Optional[str] = None
    ) -> Dict[str, Any]:
        table = dict_get(instance, self.table, use_dpath=self.use_query)

        answers = []
        if self.text_output is not None:
            answers = dict_get(instance, self.text_output, use_dpath=self.use_query)

        self.truncate_table(table_content=table, answers=answers)

        return instance

    # truncate table cells
    def truncate_table(self, table_content: Dict, answers: Optional[List]):
        cell_mapping = {}

        # One row at a time
        for row in table_content.get("rows", []):
            for i, cell in enumerate(row):
                truncated_cell = truncate_cell(cell, self.max_length)
                if truncated_cell is not None:
                    cell_mapping[cell] = truncated_cell
                    row[i] = truncated_cell

        # Update values in answer list to truncated values
        if answers is not None:
            for i, case in enumerate(answers):
                answers[i] = cell_mapping.get(case, case)


class TruncateTableRows(FieldOperator):
    """Limits table rows to specified limit by removing excess rows via random selection.

    Args:
        rows_to_keep (int) - number of rows to keep.
    """

    rows_to_keep: int = 10

    def process_value(self, table: Any) -> Any:
        return self.truncate_table_rows(table_content=table)

    def truncate_table_rows(self, table_content: Dict):
        # Get rows from table
        rows = table_content.get("rows", [])

        num_rows = len(rows)

        # if number of rows are anyway lesser, return.
        if num_rows <= self.rows_to_keep:
            return table_content

        # calculate number of rows to delete, delete them
        rows_to_delete = num_rows - self.rows_to_keep

        # Randomly select rows to be deleted
        deleted_rows_indices = random.sample(range(len(rows)), rows_to_delete)

        remaining_rows = [
            row for i, row in enumerate(rows) if i not in deleted_rows_indices
        ]
        table_content["rows"] = remaining_rows

        return table_content


class SerializeTableRowAsText(StreamInstanceOperator):
    """Serializes a table row as text.

    Args:
        fields (str) - list of fields to be included in serialization.
        to_field (str) - serialized text field name.
        max_cell_length (int) - limits cell length to be considered, optional.
    """

    fields: str
    to_field: str
    max_cell_length: Optional[int] = None

    def process(
        self, instance: Dict[str, Any], stream_name: Optional[str] = None
    ) -> Dict[str, Any]:
        linearized_str = ""
        for field in self.fields:
            value = dict_get(instance, field, use_dpath=False)
            if self.max_cell_length is not None:
                truncated_value = truncate_cell(value, self.max_cell_length)
                if truncated_value is not None:
                    value = truncated_value

            linearized_str = linearized_str + field + " is " + str(value) + ", "

        instance[self.to_field] = linearized_str
        return instance


class SerializeTableRowAsList(StreamInstanceOperator):
    """Serializes a table row as list.

    Args:
        fields (str) - list of fields to be included in serialization.
        to_field (str) - serialized text field name.
        max_cell_length (int) - limits cell length to be considered, optional.
    """

    fields: str
    to_field: str
    max_cell_length: Optional[int] = None

    def process(
        self, instance: Dict[str, Any], stream_name: Optional[str] = None
    ) -> Dict[str, Any]:
        linearized_str = ""
        for field in self.fields:
            value = dict_get(instance, field, use_dpath=False)
            if self.max_cell_length is not None:
                truncated_value = truncate_cell(value, self.max_cell_length)
                if truncated_value is not None:
                    value = truncated_value

            linearized_str = linearized_str + field + ": " + str(value) + ", "

        instance[self.to_field] = linearized_str
        return instance


class SerializeTriples(FieldOperator):
    """Serializes triples into a flat sequence.

    Sample input in expected format:
    [[ "First Clearing", "LOCATION", "On NYS 52 1 Mi. Youngsville" ], [ "On NYS 52 1 Mi. Youngsville", "CITY_OR_TOWN", "Callicoon, New York"]]

    Sample output:
    First Clearing : LOCATION : On NYS 52 1 Mi. Youngsville | On NYS 52 1 Mi. Youngsville : CITY_OR_TOWN : Callicoon, New York

    """

    def process_value(self, tripleset: Any) -> Any:
        return self.serialize_triples(tripleset)

    def serialize_triples(self, tripleset) -> str:
        return " | ".join(
            f"{subj} : {rel.lower()} : {obj}" for subj, rel, obj in tripleset
        )


class SerializeKeyValPairs(FieldOperator):
    """Serializes key, value pairs into a flat sequence.

    Sample input in expected format: {"name": "Alex", "age": 31, "sex": "M"}
    Sample output: name is Alex, age is 31, sex is M
    """

    def process_value(self, kvpairs: Any) -> Any:
        return self.serialize_kvpairs(kvpairs)

    def serialize_kvpairs(self, kvpairs) -> str:
        serialized_str = ""
        for key, value in kvpairs.items():
            serialized_str += f"{key} is {value}, "

        # Remove the trailing comma and space then return
        return serialized_str[:-2]


class ListToKeyValPairs(StreamInstanceOperator):
    """Maps list of keys and values into key:value pairs.

    Sample input in expected format: {"keys": ["name", "age", "sex"], "values": ["Alex", 31, "M"]}
    Sample output: {"name": "Alex", "age": 31, "sex": "M"}
    """

    fields: List[str]
    to_field: str
    use_query: bool = False

    def process(
        self, instance: Dict[str, Any], stream_name: Optional[str] = None
    ) -> Dict[str, Any]:
        keylist = dict_get(instance, self.fields[0], use_dpath=self.use_query)
        valuelist = dict_get(instance, self.fields[1], use_dpath=self.use_query)

        output_dict = {}
        for key, value in zip(keylist, valuelist):
            output_dict[key] = value

        instance[self.to_field] = output_dict

        return instance
