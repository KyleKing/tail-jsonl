# Roadmap

`tail-jsonl` is a lean stdin pipe filter: `<anything> | tail-jsonl` pretty-prints JSONL logs with
Rich colors. It sits in the same pipe as `kubectl logs`, docker, and local dev servers emitting
structlog/pino/LogTape output. The nearest peers are [klp](https://github.com/dloss/klp) (Python,
ergonomics-focused, though its README now points at the Rust rewrite Kelora and calls klp
unmaintained) and [hl](https://github.com/pamburus/hl) (Rust, performance-focused). This
roadmap replaces the `phases/` plan from PR #22 and records what survives from the stale
`claude/phase-0X-*` branches, what gets reimplemented differently, and what is cut.

## Guiding principles

- Stay a stdin filter. File following, multi-file time-merge, and indexing are `hl`/`lnav` territory
- Optimize per-line streaming latency at human log rates, not batch throughput. Python+Rich cannot
  win lines/sec against Rust and should not try. The harness from item 3 puts numbers on this: a
  simple record renders in roughly 190 us, a 20+ key nested one in roughly 800 us, and a mixed
  corpus streams at roughly 2,800 lines/sec. Comfortable for a live pipe, slow for a large backlog
- Filter before rendering. A discarded line should never pay Rich formatting cost
- Prefer stdlib and existing dependencies. A new runtime dependency needs a benchmark or a feature
  that cannot be reasonably built without it
- Fewer flags, better defaults. Zero-config recognition of common emitter key conventions
  (structlog, pino, zap, LogTape) is the tool's core UX

## Shipped

1. Filtering, redesigned from the PR #22 / phase-03 code
   - Keep the CLI surface and tests: `-i/--include`, `-e/--exclude`, `--field-selector KEY=PATTERN`,
     `--case-insensitive`, compiled patterns cached on `Config`
   - Toss the `console.capture()` hook that regex-matches Rich-formatted output. Match instead
     against the raw line (include/exclude) and the parsed record (field selectors), so excluded
     lines skip rendering entirely and the no-filter path stays a single straight-through call
   - Keep the `Record` -> `types.py` extraction from the local phase-01 branch (fixes the circular
     import that forced a function-local import)
2. `-l/--min-level` minimum level filter (new, in no branch). Table stakes across the category
   (`hl -l`, `klp -l`, pino-pretty) and the level is already parsed per record
3. Benchmark harness, trimmed from phase-02: `pytest-benchmark` with two scenarios (simple record,
   20+ key nested record) plus a 10k-line throughput script. No CI regression gate until the
   numbers are stable. Use it to justify or reject any future perf work (orjson, buffering)
4. Timestamp localization and formatting. Phase-06 is an unusable stub (one-line module, unused
   `arrow` dependency), so reimplement: opt-in `--local-time` and a config-level format string,
   built on stdlib `datetime.fromisoformat` + `zoneinfo`. Adopt `arrow` only if parsing coverage
   for real-world emitter formats proves insufficient
5. Key hiding: `--hide-key KEY` (repeatable, dotted-key aware). Table stakes (`pino-pretty
   --ignore`, `hl -h`, `klp -K`) and cheap given the existing dotted-key handling
6. Shell completions, generated from the argparse parser at runtime rather than phase-08's
   hand-maintained script strings (those already omit newer flags). If generation is not practical
   with argparse alone, ship none rather than static strings that drift
7. Docs refresh from phase-09, docs track only: alternatives table (hl, klp, fblog, tailspin,
   lnav), config recipes for kubectl/docker/structlog/pino, troubleshooting section. Skip the CI
   caching and line-buffering investigation unless benchmarks show a problem

Three details landed differently than written above. `zoneinfo` is unused because
`datetime.astimezone()` reaches the system zone without it, and a named target zone
(`--timezone Europe/Berlin`) is the only thing that would need it. `--local-time` leaves a
timestamp carrying no UTC offset alone, because `astimezone()` on a naive value assumes it was
written locally and would display naive-UTC logs shifted. Completions are stdlib-only rather than
`shtab`, which was evaluated and rejected because tagging actions for file completion means editing
the parser anyway.

## Now

10. One level table, not two. `corallium`'s `get_level` knows only debug/info/warn/warning/error,
    so `critical`, `fatal`, `trace`, and `notice` render as `[NOTSET]` with an added `_level_name`
    field, while `-l/--min-level` resolves those same names through a separate map in `config.py`.
    Filtering and rendering disagree about what a level is. The fix belongs upstream in corallium
11. Numeric field values. `_dot_pop` accepts only `str` and `list`, so pino's numeric `level` and
    integer epoch `time` are invisible to key detection and a pino stream needs config to render
    at all. Zero-config recognition of pino is named in the guiding principles above, so this is
    the gap between that claim and the code
12. Pruning emptied parents. Dotted extraction and `--hide-key` both remove a leaf and leave the
    container behind, rendering `server={}`. Affects `on_own_line` promotion too

## Later, if demand appears

8. Match highlighting (`-H/--highlight`), the phase-04 design. The cleanest of the feature
   branches and the ecosystem has a real gap (tailspin highlights but does not parse JSON).
   Reimplement on the redesigned pipeline since the branch code styles captured formatted output
9. Multi-line payload rendering: pretty-print `exception`/`error.stack`/embedded-JSON fields as
   real tracebacks and indented blocks. Weak across the entire ecosystem and a natural fit for the
   Python dev-server audience. Needs a design spike before committing

## Not planned

- Context lines (`-A/-B/-C`, phase-07). Niche (only klp has it), and the branch implementation
  duplicates the whole parse/format pipeline in `check_if_match`, doubling per-line work. Use
  `grep -C` before the pipe or klp for offline analysis
- Statistics summaries (`--stats`, phase-05). A different job (angle-grinder, lnav SQL); the
  implementation threads mutable state through `print_record` and is stacked on phase-04 code
- Theme registry (`--theme`, `--list-themes`, phase-08). Styles are already configurable via the
  TOML config. Document example style configs (including the branch's catppuccin values) in docs
  instead of shipping a registry, and honor `NO_COLOR`
- Time-range filtering (`--since/--until`), file follow mode, compressed input. All pull toward
  file-oriented workflows that `hl` and `lnav` already own

## Disposition of stale branches

All of these branches are deleted. Each tip is preserved as a pushed `archive/*` tag, so the diffs
stay readable (`git show archive/phase-04-highlighting:tail_jsonl/_private/highlighter.py`). PR #22
is closed. Treat the tags as reference only when reimplementing, because every branch imports
`Record` from `core`, which now lives in `types.py`.

| Branch (`claude/…`)          | Feature              | Verdict                                    |
| ---------------------------- | -------------------- | ------------------------------------------ |
| `phase-01-foundation` (PR22) | tests, filtering     | Reworked and shipped (item 1)              |
| `phase-04-highlighting`      | `-H` highlighting    | Later (item 8), reimplement                |
| `phase-05-statistics`        | `--stats`            | Cut                                        |
| `phase-06-timestamps`        | timestamp format     | Reimplemented and shipped (item 4)         |
| `phase-07-context`           | `-A/-B/-C` context   | Cut                                        |
| `phase-08-themes-completions`| themes, completions  | Themes cut; completions shipped (item 6)   |
