from src.unitxt.blocks import (
    AddFields,
    LoadHF,
    MapInstanceValues,
    RenameFields,
    SerializeTableAsIndexedRowMajor,
    TaskCard,
)
from src.unitxt.catalog import add_to_catalog
from src.unitxt.test_utils.card import test_card

# Set unitxt.settings.allow_unverified_code=True or environment vairable: UNITXT_ALLOW_UNVERIFIED_CODE to True

card = TaskCard(
    loader=LoadHF(path="ibm/tab_fact", streaming=False),
    preprocess_steps=[
        "splitters.small_no_test",
        SerializeTableAsIndexedRowMajor(field_to_field=[["table", "table_serialized"]]),
        RenameFields(
            field_to_field={"table_serialized": "text_a", "statement": "text_b"}
        ),
        MapInstanceValues(mappers={"label": {"0": "refuted", "1": "entailed"}}),
        AddFields(
            fields={
                "type_of_relation": "entailment",
                "text_a_type": "Table",
                "text_b_type": "Statement",
                "classes": ["refuted", "entailed"],
            }
        ),
    ],
    task="tasks.classification.multi_class.relation",
    templates="templates.classification.multi_class.relation.all",
)

test_card(card)
add_to_catalog(card, "cards.tab_fact", overwrite=True)
