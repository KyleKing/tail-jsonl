# tail-jsonl

Tail JSONL/NDJSON Logs

![.github/assets/demo.gif](https://raw.githubusercontent.com/KyleKing/tail-jsonl/main/.github/assets/demo.gif)

## Background

I wanted to find a tool that could:

1. Convert a stream of arbitrary JSONL logs into an easy to skim format
1. Clearly unwrap and display exceptions

`tail-jsonl` stays a stdin filter. It reads one line, prints one line, and does nothing else. If you need more than that, the tools below do more.

## Alternatives

| Tool                                             | Language | Good at                                                                                                                                                       | Reach for it instead when                                                                                                                       |
| ------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [hl](https://github.com/pamburus/hl)             | Rust     | Large JSON and logfmt files. Query expression language, chronological merge across sources with an on-disk index, follow mode, transparent gzip/xz/zstd input | Your logs live in files, you need several sources merged by time, or the volume is large enough that throughput decides the answer              |
| [klp](https://github.com/dloss/klp)              | Python   | Breadth of input formats (logfmt, JSONL, CSV, syslog, Log4j, CEF), `--where` Python expressions, grep-style context lines, pattern statistics                 | The input is not JSON, or you want `-B/-A/-C` context and ad-hoc analysis. Note the README now marks it unmaintained in favor of a Rust rewrite |
| [fblog](https://github.com/brocode/fblog)        | Rust     | The same pipe shape as `tail-jsonl`, plus Lua filter expressions and handlebars output templates                                                              | You want this workflow with custom output templates or a faster runtime                                                                         |
| [tailspin](https://github.com/bensadeh/tailspin) | Rust     | Regex highlighting of arbitrary log text (dates, URLs, UUIDs, IPs, numbers), follow mode backed by `less`                                                     | Your logs are unstructured. It colors a JSON line as text because it does not parse fields, so it cannot reformat, filter, or sort on them      |
| [lnav](https://github.com/tstack/lnav)           | C++      | Interactive investigation: merges many files by time, indexes errors, SQL and PRQL queries, JSON log format definitions with `line-format` templates          | You are digging through logs after the fact rather than watching a live pipe                                                                    |

`tail-jsonl` is Python and renders with [Rich](https://github.com/Textualize/rich), so it will lose a lines-per-second contest to any of the Rust tools. It is built for human log rates in a live pipe (a dev server, `kubectl logs -f`, `docker compose logs`), where per-line latency and zero-config key detection matter more than throughput. For a 2 GB file, use `hl`.

Other tools worth knowing: [humanlog](https://github.com/humanlogio/humanlog), [goaccess](https://goaccess.io/get-started), [angle-grinder](https://github.com/rcoh/angle-grinder#rendering), adapting [jq](https://github.com/stedolan/jq), [logss](https://github.com/todoesverso/logss), [toolong](https://github.com/Textualize/toolong), [Nerdlog](https://github.com/dimonomid/nerdlog), and [loggo](https://github.com/aurc/loggo).

## Installation

Install with [`pipx`](https://pypi.org/project/pipx), [`uv tool`](https://docs.astral.sh/uv/guides/tools), [`mise`](https://mise.jdx.dev/getting-started.html), or your other tool of choice for Python packages

```sh
# Choose one:
pipx install tail-jsonl
uv tool install tail-jsonl # or: uvx tail-jsonl
mise use -g pipx:tail-jsonl
```

## Usage

Pipe JSONL output from any file, kubernetes (such as [stern](https://github.com/stern/stern)), Docker, etc.

Tip: use `|&` to ensure that stderr and stdout are formatted (if using latest versions of zsh/bash), but all of these examples only require `|`

```sh
# Example piping input in shell
echo '{"message": "message", "timestamp": "2023-01-01T01:01:01.0123456Z", "level": "debug", "data": true, "more-data": [null, true, -123.123]}' |& tail-jsonl
cat tests/data/logs.jsonl |& tail-jsonl

# Optionally, pre-filter or format with jq, grep, awk, or other tools
cat tests/data/logs.jsonl | jq '.record' --compact-output |& tail-jsonl

# An example stern command (also consider -o=extjson)
stern envvars --context staging --container gateway --since="60m" --output raw |& tail-jsonl

# Or with Docker Compose (note that awk, cut, and grep all buffer. For awk, add '; system("")')
docker compose logs --follow | awk 'match($0, / \| \{.+/) { print substr($0, RSTART+3, RLENGTH); system("") }' |& tail-jsonl
```

For copy-pasteable pipelines (`kubectl`, Docker Compose, structlog, and pino), see [RECIPES]. If the output looks wrong or nothing appears at all, see [TROUBLESHOOTING].

### Common flags

```sh
my-app | tail-jsonl -e healthz -e '/metrics'          # drop lines matching a regex
my-app | tail-jsonl -i 'timeout|refused'              # keep only lines matching a regex
my-app | tail-jsonl -l warning                        # drop records below a level
my-app | tail-jsonl --field-selector 'service=^api$'  # keep records whose field matches
my-app | tail-jsonl --timestamp-format '%H:%M:%S'     # shorten the timestamp
my-app | tail-jsonl --hide-key pid --hide-key hostname
my-app | tail-jsonl --debug                           # show what the parser found
```

Shell completions come from the parser itself, for `bash` and `zsh`:

```sh
eval "$(tail-jsonl --completions zsh)"
```

Every flag, its TOML equivalent, and the cases where one behaves differently than you would guess are in the [CLI] reference.

## Configuration

Optionally, specify a path to a custom configuration file. For an example configuration file see: [./tests/config_default.toml](https://github.com/KyleKing/tail-jsonl/blob/main/tests/config_default.toml)

```sh
echo '...' |& tail-jsonl --config-path=~/.tail-jsonl.toml
```

The `[keys]` table is where you map an emitter's field names onto the timestamp, level, and message that `tail-jsonl` renders. [RECIPES] covers the defaults and the emitters that need mapping.

The `[filters]` and `[render]` tables hold the same settings as the filtering and rendering flags, so anything you type on every run can move into the file. A CLI flag overrides the file value for that key, and it cannot clear a value the file set. See [CLI] for the full example config and the precedence rules.

## Project Status

See the `Open Issues` and/or the [CODE_TAG_SUMMARY]. For release history, see the [CHANGELOG].

## Contributing

We welcome pull requests! For your pull request to be accepted smoothly, we suggest that you first open a GitHub issue to discuss your idea. For resources on getting started with the code base, see the below documentation:

- [DEVELOPER_GUIDE]
- [STYLE_GUIDE]

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct][contributor-covenant].

### Open Source Status

We try to reasonably meet most aspects of the "OpenSSF scorecard" from [Open Source Insights](https://deps.dev/pypi/tail-jsonl)

## Responsible Disclosure

If you have any security issue to report, please contact the project maintainers privately. You can reach us at [dev.act.kyle@gmail.com](mailto:dev.act.kyle@gmail.com).

## License

[LICENSE]

[changelog]: https://tail-jsonl.kyleking.me/docs/CHANGELOG
[cli]: https://tail-jsonl.kyleking.me/docs/CLI
[code_tag_summary]: https://tail-jsonl.kyleking.me/docs/CODE_TAG_SUMMARY
[contributor-covenant]: https://www.contributor-covenant.org
[developer_guide]: https://tail-jsonl.kyleking.me/docs/DEVELOPER_GUIDE
[license]: https://github.com/kyleking/tail-jsonl/blob/main/LICENSE
[recipes]: https://tail-jsonl.kyleking.me/docs/RECIPES
[style_guide]: https://tail-jsonl.kyleking.me/docs/STYLE_GUIDE
[troubleshooting]: https://tail-jsonl.kyleking.me/docs/TROUBLESHOOTING
