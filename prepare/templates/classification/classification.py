from src.unitxt.catalog import add_to_catalog
from src.unitxt.templates import InputOutputTemplate, MultiLabelTemplate, TemplatesList

### Multi class

add_to_catalog(
    InputOutputTemplate(
        input_format="Classify the {type_of_class} of following {text_type} to one of these options: {classes}. {text_type}: {text}",
        output_format="{label}",
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case_till_punc",
        ],
    ),
    "templates.classification.multi_class.default",
    overwrite=True,
)
add_to_catalog(
    InputOutputTemplate(  # based on "templates.classification.multi_class.default_no_instruction",
        input_format="Text: {text}",
        output_format="{label}",
        target_prefix="The {type_of_class} is ",
        instruction="Classify the {type_of_class} of the following {text_type} to one of these options: {classes}.",
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case_till_punc",
        ],
    ),
    "templates.classification.multi_class.instruction",
    overwrite=True,
)
add_to_catalog(
    InputOutputTemplate(
        input_format="{text}",
        output_format="{label}",
    ),
    "templates.classification.multi_class.empty",
    overwrite=True,
)

add_to_catalog(
    TemplatesList(
        [
            "templates.classification.multi_class.default",
            "templates.classification.multi_class.instruction",
            "templates.classification.multi_class.empty",
        ]
    ),
    "templates.classification.multi_class.all",
    overwrite=True,
)

# Multi label

add_to_catalog(
    MultiLabelTemplate(
        input_format="What are the {type_of_classes} expressed in following {text_type}?\nSelect your answer from the options: {classes}.\nIf no {type_of_classes} are expressed answer none.\nText: {text}\n{type_of_classes}: ",
        output_format="{labels}",
        labels_field="labels",
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case",
            "processors.to_list_by_comma",
            "processors.remove_none_from_list",
        ],
    ),
    "templates.classification.multi_label.default",
    overwrite=True,
)

add_to_catalog(
    MultiLabelTemplate(  # based on "templates.classification.multi_class.default_no_instruction",
        input_format="Text: {text}",
        output_format="{labels}",
        target_prefix="The {type_of_classes} is ",
        labels_field="labels",
        instruction="What are the {type_of_classes} expressed in following {text_type}?\nSelect your answer from the options: {classes}.\nIf no {type_of_classes} are expressed answer none.",
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case",
            "processors.to_list_by_comma",
            "processors.remove_none_from_list",
        ],
    ),
    "templates.classification.multi_label.instruction",
    overwrite=True,
)

add_to_catalog(
    MultiLabelTemplate(
        input_format="{text}",
        output_format="{labels}",
        labels_field="labels",
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case",
            "processors.to_list_by_comma",
            "processors.remove_none_from_list",
        ],
    ),
    "templates.classification.multi_label.empty",
    overwrite=True,
)

add_to_catalog(
    TemplatesList(
        [
            "templates.classification.multi_label.default",
            "templates.classification.multi_label.instruction",
            "templates.classification.multi_label.empty",
        ]
    ),
    "templates.classification.multi_label.all",
    overwrite=True,
)
