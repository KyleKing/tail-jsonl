## 1.4.2 (2025-09-10)

### Fix

- patch dotted key access for single line

## 1.4.1 (2025-09-06)

### Fix

- handle lists in matched fields for LogTape

## 1.4.0 (2025-09-06)

### Feat

- add defaults for LogTape

## 1.3.0 (2025-08-12)

### Feat

- include 'msg' in defaults

## 1.2.6 (2024-10-05)

### Fix

- remove beartype decorators
- remove unnecessary dependency on Pydantic
- expand ~/
- and support 'levelname'
- support 'time'
- drop support for Python 3.8
- update dependencies

### Refactor

- update dependencies
- finish pydantic v2 migration

## 1.2.5 (2023-07-23)

### Fix

- migrate to pydantic v2

## 1.2.4 (2023-06-17)

### Fix

- don't highlight non-JSONL log lines
- bump minimum pymdown dependency

## 1.2.3 (2023-03-11)

### Fix

- remove the trailing new line and formatting on raw text

## 1.2.2 (2023-02-25)

### Fix

- ensure keys are unique without losing any arguments

## 1.2.1 (2023-02-25)

### Fix

- resolve bugs in tail-jsonl config-path parsing

## 1.2.0 (2023-02-25)

### Feat

- update color scheme and resolve log issues

### Refactor

- migrate to corallium's rich_printer and styles


- begin migration to corallium and calcipy v1 with copier template

## 1.1.2 (2023-02-16)

### Fix

- show non-JSON lines

## 1.1.1 (2023-02-06)

### Feat

- use a symbol to indicate each line
- indent by four spaces on wrap
- add version arg
- indent folded text

### Fix

- bump 1.1 without release
- test loading user config and escaping dot-notation

### Refactor

- end didn't work as hoped
- switch to beartype.typing
- folded text doesn't work as expected

## 1.0.0 (2023-01-31)

### Feat

- add option for configuration file

## 0.0.1 (2023-01-30)

### Feat

- first pass at the package
- initialize the repository
