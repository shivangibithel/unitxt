from src.unitxt.catalog import add_to_catalog
from src.unitxt.templates import MultiReferenceTemplate, TemplatesList

add_to_catalog(
    MultiReferenceTemplate(
        input_format="Question: {question}",
        references_field="answers",
        target_prefix="Answer: ",
    ),
    "templates.qa.open.simple",
    overwrite=True,
)

add_to_catalog(
    MultiReferenceTemplate(
        instruction="Answer the question.\n",
        input_format="Question: {question}",
        target_prefix="Answer: ",
        references_field="answers",
    ),
    "templates.qa.open.simple2",
    overwrite=True,
)

add_to_catalog(
    TemplatesList(
        [
            "templates.qa.open.simple",
            "templates.qa.open.simple2",
        ]
    ),
    "templates.qa.open.all",
    overwrite=True,
)
