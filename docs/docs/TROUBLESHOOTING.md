# Troubleshooting

`--debug` is the first thing to reach for. It prints the parsed timestamp, level, and message for every record, and the reason any line failed to parse:

```sh
my-app | tail-jsonl --debug
```

## Nothing appears

Buffering upstream is almost always the cause. A program writing to a pipe instead of a terminal switches from line buffering to block buffering, so it holds several kilobytes of output before sending anything. The stream is not stalled, it is waiting to fill a buffer.

Fix it at the source when you can:

- Python: `python -u -m myapp`, or set `PYTHONUNBUFFERED=1` (any non-empty value works)
- Programs using C stdio: `stdbuf -oL my-app`. Recent macOS ships `stdbuf`; on older versions install coreutils and use `gstdbuf`. It has no effect on Go, Java, or CPython, because none of them buffer through libc stdio
- Programs that refuse to behave unless they see a terminal: `script -q /dev/null my-app` or `unbuffer my-app` from expect

Every stage between the source and `tail-jsonl` buffers too, and one unflushed stage is enough to stall the whole pipe:

- `grep --line-buffered`
- `jq --unbuffered`
- `awk '{print; fflush()}'`
- `sed -l` on BSD, `sed -u` on GNU

For log sources, check that you actually asked for a stream: `kubectl logs --follow`, `docker logs --follow`, `docker compose logs --follow`, `tail -f`. Without the follow flag the command prints what exists and exits, and if the container has not logged anything yet that is nothing at all.

## Lines print raw and unformatted

Any line that is not valid JSON is printed verbatim rather than dropped, which is deliberate (startup banners and stack traces from unstructured libraries still reach you). So raw output means the line was not parseable JSON. Run with `--debug` to see the parser error.

The usual causes:

- Something prepended text to the line. `kubectl logs --timestamps` and `--prefix`, and `docker compose logs` without `--no-log-prefix`, all do this. See [RECIPES] for how to strip each one
- The JSON is pretty-printed across multiple lines. `tail-jsonl` reads one record per line, so each fragment fails on its own. Compact it first with `jq -c --unbuffered .`
- The output is not JSON at all. structlog, for instance, defaults to `ConsoleRenderer` and only emits JSON once `JSONRenderer` is configured

## Timestamps or levels are not detected

A record that renders with `<no timestamp>` or `[NOTSET ]` parsed fine, but the key lookup missed. `--debug` shows what was found.

Two distinct causes. The first is a name mismatch: the emitter uses a key that is not in the default lists (`timestamp`, `time`, `record.time.repr` for timestamps, `level`, `levelname`, `record.level.name` for levels). Point the `[keys]` config at the real names:

```toml
[keys]
timestamp = ["ts", "timestamp", "time"]
level = ["severity", "level"]
message = ["msg", "message", "event"]
```

The second is a type mismatch, and no config can fix it. Only string values are used for the timestamp, level, and message, so pino's numeric `level` and epoch-millisecond `time`, or structlog's bare `TimeStamper()` float, are skipped and shown as ordinary data. Convert them upstream or with `jq` (see the pino recipe).

A level name that is not `debug`, `info`, `warn`/`warning`, or `error` renders as `[NOTSET ]` with the original value kept in a `_level_name` field. That includes `critical`, `fatal`, `trace`, and `notice`. Note that `-l/--min-level` uses a wider table than the renderer does, so `-l critical` filters correctly even though a `critical` record still renders as `NOTSET`. [CLI] explains why, and why `-l critical` keeps `trace` and `notice` records too.

## Colors are missing or mangled

Rich disables color when stdout is not a terminal, so any redirect or pipe strips it:

```sh
my-app | tail-jsonl | less        # no color
my-app | tail-jsonl > out.log     # no color
```

Set `FORCE_COLOR=1` to keep the codes, and give `less` the `-R` flag so it renders them instead of showing `ESC[38;2;...`:

```sh
my-app | FORCE_COLOR=1 tail-jsonl | less -R
```

If output is still plain, check the environment:

- `NO_COLOR` disables color whenever it is set to any non-empty string, including `NO_COLOR=0`. Unset it, or set it to the empty string
- `TERM=dumb` (or `unknown`) disables color even with `FORCE_COLOR` set
- `NO_COLOR` wins over `FORCE_COLOR`

Piping also changes the width. Rich cannot measure a pipe, so it falls back to 80 columns and wraps long records early. Set `COLUMNS` to override:

```sh
my-app | COLUMNS=200 FORCE_COLOR=1 tail-jsonl | less -R
```

[cli]: https://tail-jsonl.kyleking.me/docs/CLI
[recipes]: https://tail-jsonl.kyleking.me/docs/RECIPES
