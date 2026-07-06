# Skill: <name>

**Description:** <one sentence: what this skill does and when to use it>

**Trigger phrases:** "<phrase 1>", "<phrase 2>"

## Inputs

| Input | Required | Source |
|---|---|---|
| <input> | yes/no | <user / file path / DB table> |

## Procedure

1. <step — be explicit about file paths and commands>
2. <step>
3. Verify: <how to check the output is correct before declaring done>

## Outputs

- <file written / DB rows created / message to user, with exact paths and format>

## Example

> User: "<realistic trigger sentence>"
>
> Result: <what got created, one line>

## Failure modes

- **<what can go wrong>** → <what to do instead of failing silently>

## State & logging

- Checkpoint (if multi-step): <path under state/>
- DB records: <tables touched via scripts/db.py>
