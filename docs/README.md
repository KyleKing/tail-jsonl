# tail-jsonl

Tail JSONL/NDJSON Logs

![.github/assets/demo.gif](https://raw.githubusercontent.com/KyleKing/tail-jsonl/main/.github/assets/demo.gif)

## Background

I wanted to find a tool that could:

1. Convert a stream of arbitrary JSONL logs into an easy to skim format
1. Clearly unwrap and display exceptions

If you are looking for more functionality, there are many good alternatives: [humanlog](https://github.com/humanlogio/humanlog), [lnav](https://docs.lnav.org/en/latest/formats.html#), [goaccess](https://goaccess.io/get-started), [angle-grinder](https://github.com/rcoh/angle-grinder#rendering), adapting [jq](https://github.com/stedolan/jq), [logss](https://github.com/todoesverso/logss), [tailspin](https://github.com/bensadeh/tailspin), [toolong](https://github.com/Textualize/toolong), [Nerdlog](https://github.com/dimonomid/nerdlog), [loggo](https://github.com/aurc/loggo), etc.

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

## Configuration

Optionally, specify a path to a custom configuration file. For an example configuration file see: [./tests/config_default.toml](https://github.com/KyleKing/tail-jsonl/blob/main/tests/config_default.toml)

```sh
echo '...' |& tail-jsonl --config-path=~/.tail-jsonl.toml
```

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
[code_tag_summary]: https://tail-jsonl.kyleking.me/docs/CODE_TAG_SUMMARY
[contributor-covenant]: https://www.contributor-covenant.org
[developer_guide]: https://tail-jsonl.kyleking.me/docs/DEVELOPER_GUIDE
[license]: https://github.com/kyleking/tail-jsonl/blob/main/LICENSE
[style_guide]: https://tail-jsonl.kyleking.me/docs/STYLE_GUIDE
