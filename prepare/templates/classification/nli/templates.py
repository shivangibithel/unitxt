from src.unitxt.artifact import fetch_artifact
from src.unitxt.catalog import add_to_catalog
from src.unitxt.templates import InputOutputTemplate, TemplatesList

add_to_catalog(
    InputOutputTemplate(
        input_format="Given this sentence: {premise}, classify if this sentence: {hypothesis} is {choices}.",
        output_format="{label}",
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case_till_punc",
        ],
    ),
    "templates.classification.nli.simple",
    overwrite=True,
)

add_to_catalog(
    TemplatesList(
        [
            "templates.classification.nli.simple",
        ]
    ),
    "templates.classification.nli.all",
    overwrite=True,
)

instruction, _ = fetch_artifact("instructions.models.llama")
instruction = instruction.get_instruction()
add_to_catalog(
    InputOutputTemplate(
        input_format="Given this sentence: {premise}, classify if this sentence: {hypothesis} is {choices}.",
        output_format="{label}",
        instruction=instruction,
        postprocessors=[
            "processors.take_first_non_empty_line",
            "processors.lower_case_till_punc",
        ],
    ),
    "templates.classification.nli.simple_with_instruction_model_llama",
    overwrite=True,
)
