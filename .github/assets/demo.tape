# VHS documentation
#
# Run with:
#  vhs < .github/assets/demo.tape
#
# Output:
#   Output <path>.gif               Create a GIF output at the given <path>
#   Output <path>.mp4               Create an MP4 output at the given <path>
#   Output <path>.webm              Create a WebM output at the given <path>
#
# Settings:
#   Set FontSize <number>           Set the font size of the terminal
#   Set FontFamily <string>         Set the font family of the terminal
#   Set Height <number>             Set the height of the terminal
#   Set Width <number>              Set the width of the terminal
#   Set LetterSpacing <float>       Set the font letter spacing (tracking)
#   Set LineHeight <float>          Set the font line height
#   Set Theme <string>              Set the theme of the terminal (JSON)
#   Set Padding <number>            Set the padding of the terminal
#   Set Framerate <number>          Set the framerate of the recording
#   Set PlaybackSpeed <float>       Set the playback speed of the recording
#
# Sleep:
#   Sleep <time>                    Sleep for a set amount of <time> in seconds
#
# Type:
#   Type[@<time>] "<characters>"    Type <characters> into the terminal with a
#                                   <time> delay between each character
#
# Keys:
#   Backspace[@<time>] [number]     Press the Backspace key
#   Down[@<time>] [number]          Press the Down key
#   Enter[@<time>] [number]         Press the Enter key
#   Space[@<time>] [number]         Press the Space key
#   Tab[@<time>] [number]           Press the Tab key
#   Left[@<time>] [number]          Press the Left Arrow key
#   Right[@<time>] [number]         Press the Right Arrow key
#   Up[@<time>] [number]            Press the Up Arrow key
#   Down[@<time>] [number]          Press the Down Arrow key
#   Ctrl+<key>                      Press the Control key + <key> (e.g. Ctrl+C)
#
# Display:
#   Hide                            Hide the subsequent commands from the output
#   Show                            Show the subsequent commands in the output

Output .github/assets/demo.gif
Set PlaybackSpeed 0.5
Set TypingSpeed 10ms

Set Theme "SpaceGray Eighties"
Set FontFamily "Hack Nerd Font Mono"

Set FontSize 15
Set Width 1200
Set Height 800

Hide
Type `cd ~/Developer/packages/tail-jsonl`  Enter  Sleep 500ms
Type `echo '{"elapsed": {"repr": "0:00:00.340931", "seconds": 0.340931}, "exception": null, "extra": {"data": {"key1": 123}}, "file": {"name": "script.py", "path": "/~/Developer/packages/tail-jsonl/script.py"}, "function": "<module>", "level": "DEBUG", "level-icon": "🐞", "level-no": 10, "line": 31, "message": "debug-level log", "module": "dodo", "name": "dodo", "process": {"id": 16268, "name": "MainProcess"}, "thread": {"id": 8821244160, "name": "MainThread"}, "timestamp": "2023-01-31 06:16:00.910671-05:00"}' > debug-example.jsonl`  Enter  Sleep 500ms
Type `echo 'eyJyZWNvcmQiOiB7ImVsYXBzZWQiOiB7InJlcHIiOiAiMDowMDowMC4zNDE3NTkiLCJzZWNvbmRzIjogMC4zNDE3NTl9LCJleGNlcHRpb24iOiB7InRyYWNlYmFjayI6IHRydWUsInR5cGUiOiAiWmVyb0RpdmlzaW9uRXJyb3IiLCJ2YWx1ZSI6ICJpbnRlZ2VyIGRpdmlzaW9uIG9yIG1vZHVsbyBieSB6ZXJvIn0sImV4dHJhIjoge30sImZpbGUiOiB7Im5hbWUiOiAiZG9kby5weSIsInBhdGgiOiAiL1VzZXJzL2t5bGVraW5nL0RldmVsb3Blci9wYWNrYWdlcy90YWlsLWpzb25sL2RvZG8ucHkifSwiZnVuY3Rpb24iOiAiPG1vZHVsZT4iLCJsZXZlbCI6IHsiaWNvbiI6ICLinYwiLCJuYW1lIjogIkVSUk9SIiwibm8iOiA0MH0sImxpbmUiOiAzOCwibWVzc2FnZSI6ICJleGNlcHRpb24tbGV2ZWwgbG9nIiwibW9kdWxlIjogImRvZG8iLCJuYW1lIjogImRvZG8iLCJwcm9jZXNzIjogeyJpZCI6IDE2MjY4LCJuYW1lIjogIk1haW5Qcm9jZXNzIn0sInRocmVhZCI6IHsiaWQiOiA4ODIxMjQ0MTYwLCJuYW1lIjogIk1haW5UaHJlYWQifSwidGltZSI6IHsicmVwciI6ICIyMDIzLTAxLTMxIDA2OjE2OjAwLjkxMTQ5OS0wNTowMCIsInRpbWVzdGFtcCI6IDE2NzUxNjAxNjAuOTExNDk5fX0sInRleHQiOiAiMjAyMy0wMS0zMSAwNjoxNjowMC45MTEgfCBFUlJPUiAgICB8IGRvZG86PG1vZHVsZT46MzggLSBleGNlcHRpb24tbGV2ZWwgbG9nXG5UcmFjZWJhY2sgKG1vc3QgcmVjZW50IGNhbGwgbGFzdCk6XG5cbiAgRmlsZSBcIi4vdGFpbC1qc29ubC8udmVudi9iaW4vZG9pdFwiLCBsaW5lIDgsIGluIDxtb2R1bGU+XG4gICAgc3lzLmV4aXQobWFpbigpKVxuICAgIOKUgiAgIOKUgiAgICDilJQgPGZ1bmN0aW9uIG1haW4gYXQgMHgxMDNjM2EyYTA+XG4gICAg4pSCICAg4pSUIDxidWlsdC1pbiBmdW5jdGlvbiBleGl0PlxuICAgIOKUlCA8bW9kdWxlICdzeXMnIChidWlsdC1pbik+XG4gIEZpbGUgXCIuL3RhaWwtanNvbmwvLnZlbnYvbGliL3B5dGhvbjMuMTEvc2l0ZS1wYWNrYWdlcy9kb2l0L2NtZF9iYXNlLnB5XCIsIGxpbmUgMzk0LCBpbiBzZXR1cFxuICAgIHNlbGYubmFtZXNwYWNlID0gZGljdChpbnNwZWN0LmdldG1lbWJlcnMobG9hZGVyLmdldF9tb2R1bGUoXG4gICAg4pSUIDxkb2l0LmNtZF9iYXNlLkRvZG9UYXNrTG9hZGVyIG9iamVjdCBhdCAweDEwMmY3NDhkMD5cbiAgRmlsZSBcIi4vdGFpbC1qc29ubC8udmVudi9saWIvcHl0aG9uMy4xMS9zaXRlLXBhY2thZ2VzL2RvaXQvbG9hZGVyLnB5XCIsIGxpbmUgOTYsIGluIGdldF9tb2R1bGVcbiAgICByZXR1cm4gaW1wb3J0bGliLmltcG9ydF9tb2R1bGUob3MucGF0aC5zcGxpdGV4dChmaWxlX25hbWUpWzBdKVxuICAgICAgICAgICDilIIgICAgICAgICDilIIgICAgICAgICAgICAg4pSUIDxtb2R1bGUgJ29zJyAoZnJvemVuKT5cbiAgICAgICAgICAg4pSCICAgICAgICAg4pSUIDxmdW5jdGlvbiBpbXBvcnRfbW9kdWxlIGF0IDB4MTAyZjFjYzIwPlxuICAgICAgICAgICDilJQgPG1vZHVsZSAnaW1wb3J0bGliJyBmcm9tICcvb3B0L2hvbWVicmV3L0NlbGxhci9weXRob25AMy4xMS8zLjExLjEvRnJhbWV3b3Jrcy9QeXRob24uZnJhbWV3b3JrL1ZlcnNpb25zLzMuMTEvbGliL3B5dGhvbjMuMTEvaW0uLi5cbiAgICAgICAgICAgXG4gIEZpbGUgXCIvb3B0L2hvbWVicmV3L0NlbGxhci9weXRob25AMy4xMS8zLjExLjEvRnJhbWV3b3Jrcy9QeXRob24uZnJhbWV3b3JrL1ZlcnNpb25zLzMuMTEvbGliL3B5dGhvbjMuMTEvaW1wb3J0bGliL19faW5pdF9fLnB5XCIsIGxpbmUgMTI2LCBpbiBpbXBvcnRfbW9kdWxlXG4gICAgcmV0dXJuIF9ib290c3RyYXAuX2djZF9pbXBvcnQobmFtZVtsZXZlbDpdLCBwYWNrYWdlLCBsZXZlbClcbiAgPiBGaWxlIFwiLi90YWlsLWpzb25sL2RvZG8ucHlcIiwgbGluZSAzNiwgaW4gPG1vZHVsZT5cbiAgICAxIC8vIDBcbiAgICBcbiAgICBaZXJvRGl2aXNpb25FcnJvcjogaW50ZWdlciBkaXZpc2lvbiBvciBtb2R1bG8gYnkgemVyb1xuIn0=' | base64 --decode > exception-example.jsonl`  Enter  Sleep 500ms
Type `clear`  Enter
Show

Type `cat debug-example.jsonl`  Sleep 500ms  Enter  Sleep 1s
Type `` Enter
Type `cat debug-example.jsonl | poetry run tail-jsonl`  Sleep 500ms  Enter  Sleep 3s
Type `` Enter
Type `cat debug-example.jsonl | poetry run tail-jsonl --config-path .github/assets/demo_config.toml`  Sleep 500ms  Enter  Sleep 3s
Type `` Enter
Type `` Enter

Type `cat exception-example.jsonl`  Sleep 500ms  Enter  Sleep 1s
Type `` Enter
Type `` Enter
Type `cat exception-example.jsonl | poetry run tail-jsonl`  Sleep 500ms  Enter  Sleep 3s

Type `rm debug-example.jsonl && rm exception-example.jsonl`  Sleep 1ms  Enter
