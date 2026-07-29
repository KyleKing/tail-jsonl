# CLI Reference

Every flag `tail-jsonl` accepts, what it does, and where it will surprise you. The tool reads stdin, prints one line per input line, and exits when the stream closes.

```sh
tail-jsonl [-h] [-v] [--config-path PATH] [--debug]
[-i PATTERN] [-e PATTERN] [--field-selector KEY=PATTERN] [--case-insensitive]
[-l LEVEL] [--local-time] [--timestamp-format FORMAT] [--hide-key KEY]
[--completions SHELL]
```

Every flag except `--config-path`, `--completions`, `-h`, and `-v` has a TOML equivalent, so anything you type often can move into a config file. See [Configuration file](#configuration-file) below.

## General

`-h/--help` prints the usage above and exits. `-v/--version` prints the installed version and exits.

`--config-path PATH` points at a TOML file. `~` is expanded. There is no default location and no automatic discovery, so without this flag only the built-in defaults apply.

`--debug` prints the timestamp, level, and message that the parser extracted from each record, and the exception for any line it could not parse. Reach for it first whenever the output looks wrong. [TROUBLESHOOTING] walks through what the debug lines mean.

## Filtering

Two filters work on the raw text of the line before any parsing, and two work on the parsed record. That split decides how each one treats input that is not a JSON object.

`-i/--include PATTERN` keeps only lines matching the regex. `-e/--exclude PATTERN` drops lines matching the regex and wins over `--include`. Both take the raw line, so a pattern can match a key name, punctuation, or anything else in the text. Repeat either flag to supply several patterns, and a line passes `--include` when it matches any one of them.

`--field-selector KEY=PATTERN` keeps only records whose dotted `KEY` matches the regex. Repeat it and every selector must match. A record missing the key is dropped. The pattern is searched against the value rendered as a string, so `--field-selector attempt=^3$` works on a number.

`-l/--min-level LEVEL` drops records below the level. Accepted values are `critical`, `debug`, `error`, `info`, and `warning`, matched case-insensitively.

`--case-insensitive` applies `re.IGNORECASE` to every pattern above, including field selectors.

```sh
my-app | tail-jsonl -e healthz -e '/metrics'
my-app | tail-jsonl -l warning --field-selector 'service=^(api|worker)$'
my-app | tail-jsonl --case-insensitive -i 'timeout|refused'
```

### Sharp edges in filtering

`--min-level` keeps any record whose level it does not recognize, including records with no level key at all. That is the safe default for a stream of mixed sources (nothing vanishes silently), and it means the flag filters very little on a stream where most lines lack a `level`. It is not the same behavior as `hl -l`, which drops unknowns. Use `--field-selector level=...` when you need the strict version.

The level table used for filtering is wider than the one used for coloring. Filtering knows `critical`, `debug`, `error`, `fatal`, `info`, `warn`, and `warning`. Rendering only knows `debug`, `info`, `warn`/`warning`, and `error`, so a `critical`, `fatal`, `trace`, or `notice` record prints as `[NOTSET ]` with the original name preserved in an added `_level_name` field. The two tables interact in a way worth spelling out: `-l critical` does select your `critical` records, because they count as unrecognized and unrecognized records are kept, not because 50 is greater than or equal to 50. The same rule keeps `trace` and `notice` records under `-l critical`.

`--field-selector` matches the canonical field name, not the alias your emitter used. During parsing the first matching key from each `[keys]` list is removed from the data and moved into the timestamp, level, or message slot, so only `timestamp`, `level`, and `message` are selectable regardless of which alias appeared on the wire:

```sh
echo '{"time":"2026-01-01T01:01:01Z","level":"info","event":"foo bar"}' | tail-jsonl --field-selector message=foo   # matches
echo '{"time":"2026-01-01T01:01:01Z","level":"info","event":"foo bar"}' | tail-jsonl --field-selector event=foo     # never matches
echo '{"time":"2026-01-01T01:01:01Z","level":"info","event":"foo bar"}' | tail-jsonl --field-selector time=2026     # never matches
```

Lines that are not a JSON object print verbatim, and the record filters never drop them. That covers unparseable text and also valid JSON that is not an object, so `[1, 2]`, `"hello"`, and `42` all pass straight through `--field-selector` and `--min-level`. Only `--include` and `--exclude` can drop them, because those match the raw line.

## Rendering

`--local-time` converts parsed timestamps to the machine's local zone.

`--timestamp-format FORMAT` renders parsed timestamps with a `strftime` pattern such as `%H:%M:%S`. A timestamp that cannot be parsed is always printed verbatim, with or without this flag.

`--hide-key KEY` removes a dotted key from the trailing data. Repeat it for several keys. Hiding a key that is not present does nothing.

```sh
my-app | tail-jsonl --local-time --timestamp-format '%H:%M:%S'
my-app | tail-jsonl --hide-key pid --hide-key hostname --hide-key request.headers
```

### Sharp edges in rendering

`--local-time` does nothing to a timestamp that carries no UTC offset, because the zone it was written in is unknown and guessing would move the value by hours. On a stream of naive timestamps the flag looks broken when it is refusing to invent information:

```text
{"timestamp": "2026-01-01T01:01:01"}   --local-time -->  2026-01-01T01:01:01          (unchanged)
{"timestamp": "2026-01-01T01:01:01Z"}  --local-time -->  2025-12-31T19:01:01-06:00
```

`--timestamp-format` fills in a time portion that the source never had. A date-only value parses to midnight, so `2026-01-01` under `%Y-%m-%d %H:%M:%S` renders as `2026-01-01 00:00:00`.

`--hide-key` on a nested leaf leaves the emptied parent behind. Hiding the only child of `server` renders `server={}`, so hide the parent when you want the whole branch gone:

```sh
echo '{"message":"m","server":{"host":"h"}}' | tail-jsonl --hide-key server.host  # m server={}
echo '{"message":"m","server":{"host":"h"}}' | tail-jsonl --hide-key server       # m
```

`--hide-key` cannot hide the timestamp, level, or message. Those values are pulled out of the data during parsing and rendered in their own slots, so by the time hiding runs there is nothing left under those names to remove. `--hide-key timestamp` on a record whose timestamp key is `timestamp` is a no-op, and on a record that has a leftover `timestamp` string in the data it would remove that instead.

## Shell completions

`--completions SHELL` writes a completion script to stdout and exits. Only `bash` and `zsh` are supported, and the script is generated from the parser itself, so it always matches the installed version.

The quickest setup is an `eval` in your shell rc file:

```sh
# ~/.zshrc
eval "$(tail-jsonl --completions zsh)"

# ~/.bashrc
eval "$(tail-jsonl --completions bash)"
```

That costs one subprocess per shell startup. To avoid it, write the script into a directory your shell already loads:

```sh
# zsh, into any directory on $fpath
tail-jsonl --completions zsh > ~/.zfunc/_tail-jsonl

# bash
tail-jsonl --completions bash > /usr/local/etc/bash_completion.d/tail-jsonl
```

Regenerate the file after upgrading `tail-jsonl`, because a cached script does not know about flags added since it was written.

## Configuration file

A config file collects the flags you always pass, plus the `[keys]` and `[styles]` tables that have no CLI equivalent. Load it with `--config-path`. Every table and every key is optional, and anything you leave out keeps its default.

```toml
debug = false

[keys]
timestamp = ["timestamp", "time", "record.time.repr"]
level = ["level", "levelname", "record.level.name"]
message = ["event", "message", "msg", "record.message"]
on_own_line = ["text", "exception", "error.stack"]

[filters]
include = []
exclude = ["healthz", "/metrics"]
field_selectors = ["service=^(api|worker)$"]
case_insensitive = true
min_level = "info"

[render]
local_time = true
timestamp_format = "%H:%M:%S"
hidden_keys = ["pid", "hostname", "request.headers"]

[styles]
timestamp = "#8DAAA1"
message = "bold"
key = "#8DAAA1"
value = "#A28EAB"
value_own_line = "#AAA18D"

[styles.colors]
level_error = "#e77d8f"
level_warn = "#d8b172"
level_info = "#a8cd76"
level_debug = "#82a1f1"
level_fallback = "#b69bf1"
```

The values shown for `[keys]` and `[styles]` are the defaults. `[filters]` and `[render]` default to empty lists, `false`, and unset.

### Flags and their TOML keys

| Flag                 | TOML key                   |
| -------------------- | -------------------------- |
| `--debug`            | `debug`                    |
| `-i/--include`       | `filters.include`          |
| `-e/--exclude`       | `filters.exclude`          |
| `--field-selector`   | `filters.field_selectors`  |
| `--case-insensitive` | `filters.case_insensitive` |
| `-l/--min-level`     | `filters.min_level`        |
| `--local-time`       | `render.local_time`        |
| `--timestamp-format` | `render.timestamp_format`  |
| `--hide-key`         | `render.hidden_keys`       |

`--config-path` and `--completions` have no TOML equivalent, and `[keys]` and `[styles]` have no CLI equivalent. [RECIPES] covers `[keys]` in depth, because that table is what most emitters need.

### Precedence

A CLI flag overrides the config file value for that key only. The other keys keep whatever the file set. For the list flags the CLI value replaces the file's list rather than appending to it, so `-e HEALTHZ` on a config that sets `exclude = ["healthz", "/metrics"]` leaves you excluding only `HEALTHZ`.

A CLI flag can never clear a value the file set. Every option falls back to the file value when the flag is absent, and the boolean flags only turn things on, so `case_insensitive = true` in the file cannot be switched off from the command line. If you need a run without a setting, drop `--config-path` or point it at a second file.

Bad input is rejected at startup rather than per line. An unparseable regex, a selector missing its `=`, an unknown level, or an unparseable dotted key exits with a usage error before the first line is read.

[recipes]: https://tail-jsonl.kyleking.me/docs/RECIPES
[troubleshooting]: https://tail-jsonl.kyleking.me/docs/TROUBLESHOOTING
