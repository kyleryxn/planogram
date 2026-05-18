import base64
import json

from anthropic import Anthropic

from planogram.models import ScheduleEvent

TRANSCRIBE_PROMPT = """\
Look at this work schedule grid. Read it one date column at a time, left to right.

For each date column that has at least one shift written in it:
  - Write the date from the column header on its own line, prefixed with "DATE:"
  - Then, for every non-blank cell in that column from top to bottom, write one line:
      [row label] | [start time] | [end time]
    where [row label] is exactly what is written in the leftmost column of that row.
    If the leftmost column for that row is blank, empty, or says something like
    "open" / "available" / "unassigned", use the label UNASSIGNED.

Do NOT borrow a name from a nearby row — use only what is on the same row.
Skip columns where every cell is blank.
Skip individual blank cells within a column.
"""

EXTRACT_PROMPT = """\
Convert the following schedule text into a JSON array of calendar events.

Rules:
- Output ONLY a valid JSON array. No explanation, no markdown fences.
- Each event must have: "title" (string), "date" (YYYY-MM-DD), "start_time" (HH:MM 24h).
- Optional fields: "end_time" (HH:MM 24h), "description" (string), "location" (string).
- If a year is not shown, assume {year}.
- If you are unsure about a time, omit that event rather than guess.
- If there are no events, output: []

Schedule text:
{transcription}
"""


def _transcribe(client: Anthropic, image_source: dict) -> str:
    msg = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": image_source},
                    {"type": "text", "text": TRANSCRIBE_PROMPT},
                ],
            }
        ],
    )
    return msg.content[0].text.strip()


def _to_pipe_lines(column_text: str) -> list[str]:
    """Convert column-format output to NAME | DATE | START | END lines."""
    result = []
    current_date = ""
    for raw in column_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.upper().startswith("DATE:"):
            current_date = line[5:].strip()
        elif "|" in line and current_date:
            parts = [p.strip() for p in line.split("|")]
            name = parts[0] if len(parts) > 0 else ""
            start = parts[1] if len(parts) > 1 else ""
            end = parts[2] if len(parts) > 2 else ""
            result.append(f"{name} | {current_date} | {start} | {end}")
    return result


def _filter_lines(lines: list[str], person_name: str) -> list[str]:
    """Keep only lines whose NAME field contains any word from person_name."""
    name_parts = [p.lower() for p in person_name.split() if p]
    kept = []
    for line in lines:
        name_field = line.split("|")[0].strip().lower()
        if any(part in name_field for part in name_parts):
            kept.append(line)
    return kept



def parse_events(
    image_bytes: bytes,
    media_type: str,
    api_key: str,
    today: str,
    person_name: str | None = None,
) -> tuple[list[ScheduleEvent], str]:
    client = Anthropic(api_key=api_key)
    year = today[:4]
    image_source = {
        "type": "base64",
        "media_type": media_type,
        "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
    }

    # Pass 1 — column-by-column visual transcription
    raw_transcription = _transcribe(client, image_source)

    # Convert to flat NAME | DATE | START | END lines, then optionally filter
    pipe_lines = _to_pipe_lines(raw_transcription)
    if person_name:
        filtered = _filter_lines(pipe_lines, person_name)
        transcription = "\n".join(filtered) if filtered else "\n".join(pipe_lines)
    else:
        transcription = "\n".join(pipe_lines)

    # Pass 2 — convert to structured JSON
    extract_msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": EXTRACT_PROMPT.format(transcription=transcription, year=year),
            }
        ],
    )

    raw = extract_msg.content[0].text.strip()
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON array found in response:\n{raw}")

    try:
        event_dicts = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Claude returned invalid JSON: {exc}\n\nRaw response:\n{raw}"
        ) from exc

    events = [ScheduleEvent.model_validate(ev) for ev in event_dicts]
    return events, raw_transcription
