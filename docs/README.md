# tail-jsonl

Tail JSONL Logs

## Background

I wanted to find a tool that could:

1. Convert a stream of JSONL logs into a readable `logfmt`-like output with minimal configuration
1. Show exceptions on their own line

I investigated a lot of alternatives such as: [humanlog](https://github.com/humanlogio/humanlog), [lnav](https://docs.lnav.org/en/latest/formats.html#), [goaccess](https://goaccess.io/get-started), [angle-grinder](https://github.com/rcoh/angle-grinder#rendering), [jq](https://github.com/stedolan/jq), [textualog](https://github.com/rhuygen/textualog), etc. but None had the exception formatting I wanted.

## Installation

```sh
pipx install tail-jsonl
```

## Usage

```sh
echo '{"message": "message", "timestamp": "2023-01-01T01:01:01.0123456Z", "level": "debug", "data": true, "more-data": [null, true, -123.123]}' | tail-jsonl
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

We try to reasonably meet most aspects of the "OpenSSF scorecard" from [Open Source Insights](https://deps.dev/pypi/tail_jsonl)

## Responsible Disclosure

If you have any security issue to report, please contact the project maintainers privately. You can reach us at [dev.act.kyle@gmail.com](mailto:dev.act.kyle@gmail.com).

## License

[LICENSE]

[changelog]: ./docs/CHANGELOG.md
[code_tag_summary]: ./docs/CODE_TAG_SUMMARY.md
[contributor-covenant]: https://www.contributor-covenant.org
[developer_guide]: ./docs/DEVELOPER_GUIDE.md
[license]: https://github.com/kyleking/tail-jsonl/LICENSE
[style_guide]: ./docs/STYLE_GUIDE.md
