from poml import poml

from chattr.app.settings import Settings


def _setup_prompt(settings: Settings) -> str:
    prompt_template = poml(
        settings.directory.prompts / "template.poml",
        {"character": "Napoleon"},
        chat=False,
        format="dict",
    )
    if not isinstance(prompt_template, dict):
        _msg = "Prompt template must be a string."
        raise TypeError(_msg)
    return prompt_template["messages"]
