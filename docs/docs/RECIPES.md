# Recipes

Working invocations for the pipelines `tail-jsonl` is most often dropped into, plus the `[keys]` config each one needs (when it needs any).

## What is recognized without configuration

`tail-jsonl` looks for the first matching key in each list and renders everything else as trailing `key=value` pairs:

| Field     | Keys searched, in order                     |
| --------- | ------------------------------------------- |
| timestamp | `timestamp`, `time`, `record.time.repr`     |
| level     | `level`, `levelname`, `record.level.name`   |
| message   | `event`, `message`, `msg`, `record.message` |
| own line  | `text`, `exception`, `error.stack`          |

Keys are parsed with dot notation, so `record.time.repr` reaches into a nested object. Override any of these lists in a TOML file and pass it with `--config-path`. A list you do not set keeps its default. The rest of the config file, and every CLI flag, is documented in [CLI].

One constraint is worth knowing before you write a config. Strings, numbers, booleans, and lists are all picked up for the timestamp, level, and message, but a nested object is not, because an object is not a value. An epoch number in the timestamp slot is converted to ISO-8601 automatically. A numeric level is shown as the number with no color, since 30 means info to pino and warning to Python's `logging`, and only you can say which.

## Kubernetes

Most Kubernetes workloads write JSON straight to stdout, so nothing needs mapping:

```sh
kubectl logs --follow deploy/api |& tail-jsonl
kubectl logs --follow -l app=api --max-log-requests 20 --since=15m |& tail-jsonl
```

Skip `--timestamps` and `--prefix`. Both prepend text to every line (`--timestamps` an RFC3339Nano stamp, `--prefix` a `[pod/NAME/CONTAINER] ` label), which makes the line invalid JSON and gets it printed verbatim. If you need the pod label to tell replicas apart, strip it back off before the pipe:

```sh
kubectl logs --follow -l app=api --prefix | grep --line-buffered -o '{.*}' |& tail-jsonl
```

[stern](https://github.com/stern/stern) is the friendlier multi-pod option, and `--output raw` gives it the same shape:

```sh
stern envvars --context staging --container gateway --since=60m --output raw |& tail-jsonl
```

If your cluster's apps emit Go-style keys such as `ts` and `severity`, map them once:

```toml
[keys]
timestamp = ["ts", "timestamp", "time"]
level = ["severity", "level"]
message = ["msg", "message", "event"]
on_own_line = ["stacktrace", "exception", "error.stack"]
```

## Docker and Docker Compose

`docker logs` passes the container's stdout through unchanged, so it needs nothing:

```sh
docker logs --follow api |& tail-jsonl
```

`docker compose logs` is different. It prefixes every line with the container name padded to a common width and then a space-padded pipe separator, which breaks JSON parsing. Turn the prefix off:

```sh
docker compose logs --follow --no-log-prefix api |& tail-jsonl
```

`--no-color` only drops the ANSI codes and keeps the prefix, so it is not a substitute. When you are watching several services at once and want the prefix kept upstream, cut it out on the way in:

```sh
docker compose logs --follow | awk '{sub(/^[^|]* \| /, ""); print; fflush()}' |& tail-jsonl
```

The `fflush()` matters, because without it `awk` buffers a block at a time and the pipe goes quiet between bursts. `sed` can do the same substitution, but the flag that makes it flush per line differs between BSD and GNU (`-l` versus `-u`), so `awk` travels better. See [TROUBLESHOOTING] for the rest of the buffering story.

## structlog

structlog's JSON output maps onto the defaults with no config at all, as long as you configure the timestamper for ISO strings:

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
)
```

That emits `{"event": ..., "level": "warning", "timestamp": "2026-07-29T12:49:37.903273Z"}`, and `event`, `level`, and `timestamp` are all defaults. `format_exc_info` writes the traceback into `exception` as a string, which is a default `on_own_line` key, so exceptions print unwrapped below the message.

One thing to watch. structlog's out-of-the-box configuration uses `ConsoleRenderer`, not `JSONRenderer`, so a project that never calls `structlog.configure()` is emitting human-formatted text that `tail-jsonl` will pass through untouched. A bare `TimeStamper()` with no `fmt` emits a float UNIX timestamp, which needs no special handling because epoch values are converted for you.

Run the app unbuffered so lines arrive as they are written:

```sh
python -u -m myapp |& tail-jsonl
```

## pino

pino is the one common emitter whose defaults do not map cleanly. A default line looks like this:

```text
{"level":30,"time":1785329450889,"pid":24429,"hostname":"host","msg":"hello"}
```

`msg` and `time` are already in the default key lists, so this renders without any config: `time` is epoch milliseconds and becomes an ISO-8601 timestamp, and `level` shows as `30`. What you lose is severity. pino numbers its levels 10 trace, 20 debug, 30 info, 40 warn, 50 error, 60 fatal, and `tail-jsonl` will not assume that scale, so a numeric level gets no color and `-l/--min-level` cannot compare it.

To get color and filtering back, emit level names on the pino side (v9 and v10 syntax, `useLevelLabels` was removed):

```js
const logger = pino({
    timestamp: pino.stdTimeFunctions.isoTime,
    formatters: {
        level(label) {
            return {
                level: label
            }
        }
    },
})
```

That gives `{"level":"warn","time":"2026-07-29T12:50:50.890Z",...}`, which needs no `[keys]` config. Note that `formatters` are not applied when pino writes through a transport running in a worker thread, so levels can still arrive as numbers in that setup.

When you cannot change the application, map the level in the pipe:

```sh
node server.js | jq -c --unbuffered '
  .level |= ({"10":"trace","20":"debug","30":"info","40":"warn","50":"error","60":"fatal"}[tostring] // .)
' |& tail-jsonl
```

`--unbuffered` keeps `jq` flushing per line. Every pino level name maps straight across, `trace` and `fatal` included, so nothing needs collapsing. There is no `.time` clause because epoch values are already handled.

## Nested payloads

Dotted keys reach into nested objects, so a wrapped record maps fine:

```toml
[keys]
timestamp = ["log.time"]
level = ["log.level"]
message = ["log.msg"]
```

The extracted values are removed from the nested object, which is then rendered as whatever is left. A wrapper the extraction empties is dropped along with the keys, so `log={}` never appears.

[cli]: https://tail-jsonl.kyleking.me/docs/CLI
[troubleshooting]: https://tail-jsonl.kyleking.me/docs/TROUBLESHOOTING
