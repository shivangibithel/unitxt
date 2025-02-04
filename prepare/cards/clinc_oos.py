from datasets import get_dataset_config_names, load_dataset_builder

from src.unitxt import add_to_catalog
from src.unitxt.blocks import (
    AddFields,
    LoadHF,
    MapInstanceValues,
    RenameFields,
    TaskCard,
)
from src.unitxt.test_utils.card import test_card

dataset_name = "clinc_oos"

for subset in get_dataset_config_names(dataset_name):
    ds_builder = load_dataset_builder(dataset_name, subset)
    classlabels = ds_builder.info.features["intent"]
    map_label_to_text = {
        str(i): label.replace("_", " ") for i, label in enumerate(classlabels.names)
    }
    classes = [label.replace("_", " ") for label in classlabels.names]

    card = TaskCard(
        loader=LoadHF(path=dataset_name, name=subset),
        preprocess_steps=[
            RenameFields(field_to_field={"intent": "label"}),
            MapInstanceValues(mappers={"label": map_label_to_text}),
            AddFields(
                fields={
                    "classes": classes,
                    "text_type": "sentence",
                    "type_of_class": "intent",
                }
            ),
        ],
        task="tasks.classification.multi_class",
        templates="templates.classification.multi_class.all",
    )
    test_card(card, debug=False)
    add_to_catalog(artifact=card, name=f"cards.{dataset_name}.{subset}", overwrite=True)
