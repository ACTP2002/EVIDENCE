import json
import os
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# You will replace these imports with your DeepAgents entrypoints.
# The idea: load the skill prompt (skill.md), feed input, parse JSON output, validate.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

SKILL_MD_PATH = "skills/timeline-reconstruction-engine/SKILL.md"
INPUT_PATH = "test_case.json"
SCHEMA_PATH = "skills/timeline-reconstruction-engine/schemas/timeline_output.schema.json"

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    skill_md = read_text(SKILL_MD_PATH)
    case_input = read_json(INPUT_PATH)
    schema = read_json(SCHEMA_PATH)

    llm = ChatGoogleGenerativeAI(
    model=os.environ.get("GEMINI_MODEL", "models/gemini-2.5-flash-lite"),
    temperature=0
    )

    messages = [
        SystemMessage(content=skill_md),
        SystemMessage(
        content=(
            "When producing JSON output, return raw JSON only. "
            "Do NOT wrap the response in Markdown code fences such as ```json or ```."
            )
        ),
        HumanMessage(content=json.dumps(case_input, ensure_ascii=False))
    ]

    resp = llm.invoke(messages).content

    # Expect strict JSON output
    try:
        output = json.loads(resp)
    except json.JSONDecodeError:
        raise SystemExit(f"Model did not return valid JSON. Raw output:\n{resp}")

    # Validate output schema
    try:
        validate(instance=output, schema=schema)
    except ValidationError as e:
        raise SystemExit(f"Output JSON failed schema validation:\n{e}\n\nOutput:\n{json.dumps(output, indent=2)}")

    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
