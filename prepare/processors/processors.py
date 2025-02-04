from src.unitxt import add_to_catalog
from src.unitxt.logging_utils import get_logger
from src.unitxt.operator import SequentialOperator
from src.unitxt.operators import RemoveValues
from src.unitxt.processors import (
    ConvertToBoolean,
    FirstCharacter,
    LowerCase,
    LowerCaseTillPunc,
    StanceToProCon,
    StringOrNotString,
    TakeFirstNonEmptyLine,
    TakeFirstWord,
    ToYesOrNone,
    YesNoToInt,
)

logger = get_logger()

add_to_catalog(
    SequentialOperator(
        steps=[
            TakeFirstNonEmptyLine(field="prediction", process_every_value=False),
            TakeFirstNonEmptyLine(field="references", process_every_value=True),
        ]
    ),
    "processors.take_first_non_empty_line",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            LowerCaseTillPunc(field="prediction", process_every_value=False),
            LowerCaseTillPunc(field="references", process_every_value=True),
        ]
    ),
    "processors.lower_case_till_punc",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            StringOrNotString(
                string="hate speech", field="prediction", process_every_value=False
            ),
            StringOrNotString(
                string="hate speech", field="references", process_every_value=True
            ),
        ]
    ),
    "processors.hate_speech_or_not_hate_speech",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            LowerCase(field="prediction", process_every_value=False),
            LowerCase(field="references", process_every_value=True),
        ]
    ),
    "processors.lower_case",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            StringOrNotString(
                string="toxic", field="prediction", process_every_value=False
            ),
            StringOrNotString(
                string="toxic", field="references", process_every_value=True
            ),
        ]
    ),
    "processors.toxic_or_not_toxic",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            ConvertToBoolean(field="prediction", process_every_value=False),
            ConvertToBoolean(field="references", process_every_value=True),
        ]
    ),
    "processors.convert_to_boolean",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            TakeFirstWord(field="prediction", process_every_value=False),
            TakeFirstWord(field="references", process_every_value=True),
        ]
    ),
    "processors.take_first_word",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            YesNoToInt(field="prediction", process_every_value=False),
            YesNoToInt(field="references", process_every_value=True),
        ]
    ),
    "processors.yes_no_to_int",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            ToYesOrNone(field="prediction", process_every_value=False),
            ToYesOrNone(field="references", process_every_value=True),
        ]
    ),
    "processors.to_yes_or_none",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            StanceToProCon(field="prediction", process_every_value=False),
            StanceToProCon(field="references", process_every_value=True),
        ]
    ),
    "processors.stance_to_pro_con",
    overwrite=True,
)


parser = FirstCharacter(field="TBD")
example = " A. This is the answer."
logger.info(parser.process_value(example))
assert parser.process_value(example) == "A"

example = "   "
logger.info(parser.process_value(example))
assert parser.process_value(example) == ""

add_to_catalog(
    SequentialOperator(
        steps=[
            FirstCharacter(field="prediction", process_every_value=False),
            FirstCharacter(field="references", process_every_value=True),
        ]
    ),
    "processors.first_character",
    overwrite=True,
)

add_to_catalog(
    SequentialOperator(
        steps=[
            RemoveValues(
                field="prediction",
                unallowed_values=["none"],
                process_every_value=False,
            ),
            RemoveValues(
                field="references/*",
                unallowed_values=["none"],
                process_every_value=False,
                use_query=True,
            ),
        ]
    ),
    "processors.remove_none_from_list",
    overwrite=True,
)
