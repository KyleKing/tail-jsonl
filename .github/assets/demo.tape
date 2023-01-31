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
Type `echo '{"elapsed": {"repr": "0:00:00.340931", "seconds": 0.340931}, "exception": null, "extra": {"data": {"key1": 123}}, "file": {"name": "script.py", "path": "/~/Developer/packages/tail-jsonl/script.py"}, "function": "<module>", "level": "DEBUG", "level-icon": "🐞", "level-no": 10, "line": 31, "message": "debug-level log", "module": "dodo", "name": "dodo", "process": {"id": 16268, "name": "MainProcess"}, "thread": {"id": 8821244160, "name": "MainThread"}, "timestamp": "2023-01-31 06:16:00.910671-05:00"}' > .logs/debug-example.jsonl`  Enter  Sleep 500ms
Type `echo 'eyJ0ZXh0IjogIjIwMjMtMDEtMzEgMDY6MTY6MDAuOTExIHwgRVJST1IgICAgfCBkb2RvOjxtb2R1bGU+OjM4IC0gZXhjZXB0aW9uLWxldmVsIGxvZ1xuVHJhY2ViYWNrIChtb3N0IHJlY2VudCBjYWxsIGxhc3QpOlxuXG4gIEZpbGUgXCIvVXNlcnMva3lsZWtpbmcvRGV2ZWxvcGVyL3BhY2thZ2VzL3RhaWwtanNvbmwvLnZlbnYvYmluL2RvaXRcIiwgbGluZSA4LCBpbiA8bW9kdWxlPlxuICAgIHN5cy5leGl0KG1haW4oKSlcbiAgICDilIIgICDilIIgICAg4pSUIDxmdW5jdGlvbiBtYWluIGF0IDB4MTAzYzNhMmEwPlxuICAgIOKUgiAgIOKUlCA8YnVpbHQtaW4gZnVuY3Rpb24gZXhpdD5cbiAgICDilJQgPG1vZHVsZSAnc3lzJyAoYnVpbHQtaW4pPlxuICBGaWxlIFwiL1VzZXJzL2t5bGVraW5nL0RldmVsb3Blci9wYWNrYWdlcy90YWlsLWpzb25sLy52ZW52L2xpYi9weXRob24zLjExL3NpdGUtcGFja2FnZXMvZG9pdC9fX21haW5fXy5weVwiLCBsaW5lIDgsIGluIG1haW5cbiAgICBzeXMuZXhpdChEb2l0TWFpbigpLnJ1bihzeXMuYXJndlsxOl0pKVxuICAgIOKUgiAgIOKUgiAgICDilIIgICAgICAgICAgICAgIOKUgiAgIOKUlCBbJy9Vc2Vycy9reWxla2luZy9EZXZlbG9wZXIvcGFja2FnZXMvdGFpbC1qc29ubC8udmVudi9iaW4vZG9pdCcsICdydW4nLCAndGVzdCddXG4gICAg4pSCICAg4pSCICAgIOKUgiAgICAgICAgICAgICAg4pSUIDxtb2R1bGUgJ3N5cycgKGJ1aWx0LWluKT5cbiAgICDilIIgICDilIIgICAg4pSUIDxjbGFzcyAnZG9pdC5kb2l0X2NtZC5Eb2l0TWFpbic+XG4gICAg4pSCICAg4pSUIDxidWlsdC1pbiBmdW5jdGlvbiBleGl0PlxuICAgIOKUlCA8bW9kdWxlICdzeXMnIChidWlsdC1pbik+XG4gIEZpbGUgXCIvVXNlcnMva3lsZWtpbmcvRGV2ZWxvcGVyL3BhY2thZ2VzL3RhaWwtanNvbmwvLnZlbnYvbGliL3B5dGhvbjMuMTEvc2l0ZS1wYWNrYWdlcy9kb2l0L2RvaXRfY21kLnB5XCIsIGxpbmUgMjk0LCBpbiBydW5cbiAgICByZXR1cm4gY29tbWFuZC5wYXJzZV9leGVjdXRlKGFyZ3MpXG4gICAgICAgICAgIOKUgiAgICAgICDilIIgICAgICAgICAgICAg4pSUIFsndGVzdCddXG4gICAgICAgICAgIOKUgiAgICAgICDilJQgPGZ1bmN0aW9uIENvbW1hbmQucGFyc2VfZXhlY3V0ZSBhdCAweDEwMzdlMGZlMD5cbiAgICAgICAgICAg4pSUIDxkb2l0LmNtZF9ydW4uUnVuIG9iamVjdCBhdCAweDEwMzg3NmY1MD5cbiAgRmlsZSBcIi9Vc2Vycy9reWxla2luZy9EZXZlbG9wZXIvcGFja2FnZXMvdGFpbC1qc29ubC8udmVudi9saWIvcHl0aG9uMy4xMS9zaXRlLXBhY2thZ2VzL2RvaXQvY21kX2Jhc2UucHlcIiwgbGluZSAxNTAsIGluIHBhcnNlX2V4ZWN1dGVcbiAgICByZXR1cm4gc2VsZi5leGVjdXRlKHBhcmFtcywgYXJncylcbiAgICAgICAgICAg4pSCICAgIOKUgiAgICAgICDilIIgICAgICAg4pSUIFsndGVzdCddXG4gICAgICAgICAgIOKUgiAgICDilIIgICAgICAg4pSUIHsnZGVwX2ZpbGUnOiAnLmRvaXQuZGInLCAnYmFja2VuZCc6ICdkYm0nLCAnY29kZWNfY2xzJzogJ2pzb24nLCAnY2hlY2tfZmlsZV91cHRvZGF0ZSc6ICdtZDUnLCAnZG9kb0ZpbGUnOiAnZG9kby5weScsICdjd2RQYXRoLi4uXG4gICAgICAgICAgIOKUgiAgICDilJQgPGZ1bmN0aW9uIERvaXRDbWRCYXNlLmV4ZWN1dGUgYXQgMHgxMDM3ZTFkYTA+XG4gICAgICAgICAgIOKUlCA8ZG9pdC5jbWRfcnVuLlJ1biBvYmplY3QgYXQgMHgxMDM4NzZmNTA+XG4gIEZpbGUgXCIvVXNlcnMva3lsZWtpbmcvRGV2ZWxvcGVyL3BhY2thZ2VzL3RhaWwtanNvbmwvLnZlbnYvbGliL3B5dGhvbjMuMTEvc2l0ZS1wYWNrYWdlcy9kb2l0L2NtZF9iYXNlLnB5XCIsIGxpbmUgNTI0LCBpbiBleGVjdXRlXG4gICAgc2VsZi5sb2FkZXIuc2V0dXAocGFyYW1zKVxuICAgIOKUgiAgICDilIIgICAgICDilIIgICAgIOKUlCB7J2RlcF9maWxlJzogJy5kb2l0LmRiJywgJ2JhY2tlbmQnOiAnZGJtJywgJ2NvZGVjX2Nscyc6ICdqc29uJywgJ2NoZWNrX2ZpbGVfdXB0b2RhdGUnOiAnbWQ1JywgJ2RvZG9GaWxlJzogJ2RvZG8ucHknLCAnY3dkUGF0aC4uLlxuICAgIOKUgiAgICDilIIgICAgICDilJQgPGZ1bmN0aW9uIERvZG9UYXNrTG9hZGVyLnNldHVwIGF0IDB4MTAzN2UxODAwPlxuICAgIOKUgiAgICDilJQgPGRvaXQuY21kX2Jhc2UuRG9kb1Rhc2tMb2FkZXIgb2JqZWN0IGF0IDB4MTAyZjc0OGQwPlxuICAgIOKUlCA8ZG9pdC5jbWRfcnVuLlJ1biBvYmplY3QgYXQgMHgxMDM4NzZmNTA+XG4gIEZpbGUgXCIvVXNlcnMva3lsZWtpbmcvRGV2ZWxvcGVyL3BhY2thZ2VzL3RhaWwtanNvbmwvLnZlbnYvbGliL3B5dGhvbjMuMTEvc2l0ZS1wYWNrYWdlcy9kb2l0L2NtZF9iYXNlLnB5XCIsIGxpbmUgMzk0LCBpbiBzZXR1cFxuICAgIHNlbGYubmFtZXNwYWNlID0gZGljdChpbnNwZWN0LmdldG1lbWJlcnMobG9hZGVyLmdldF9tb2R1bGUoXG4gICAg4pSCICAgIOKUgiAgICAgICAgICAgICAgICDilIIgICAgICAg4pSCICAgICAgICAgIOKUgiAgICAgIOKUlCA8ZnVuY3Rpb24gZ2V0X21vZHVsZSBhdCAweDEwMmY2ZmNlMD5cbiAgICDilIIgICAg4pSCICAgICAgICAgICAgICAgIOKUgiAgICAgICDilIIgICAgICAgICAg4pSUIDxtb2R1bGUgJ2RvaXQubG9hZGVyJyBmcm9tICcvVXNlcnMva3lsZWtpbmcvRGV2ZWxvcGVyL3BhY2thZ2VzL3RhaWwtanNvbmwvLnZlbnYvbGliL3B5dGhvbjMuMTEvc2l0ZS1wYWNrYWdlcy9kb2l0L2xvYWRlci5weSc+XG4gICAg4pSCICAgIOKUgiAgICAgICAgICAgICAgICDilIIgICAgICAg4pSUIDxmdW5jdGlvbiBnZXRtZW1iZXJzIGF0IDB4MTAyZjFkYmMwPlxuICAgIOKUgiAgICDilIIgICAgICAgICAgICAgICAg4pSUIDxtb2R1bGUgJ2luc3BlY3QnIGZyb20gJy9vcHQvaG9tZWJyZXcvQ2VsbGFyL3B5dGhvbkAzLjExLzMuMTEuMS9GcmFtZXdvcmtzL1B5dGhvbi5mcmFtZXdvcmsvVmVyc2lvbnMvMy4xMS9saWIvcHl0aG9uMy4xMS9pbnNwLi4uXG4gICAg4pSCICAgIOKUlCBOb25lXG4gICAg4pSUIDxkb2l0LmNtZF9iYXNlLkRvZG9UYXNrTG9hZGVyIG9iamVjdCBhdCAweDEwMmY3NDhkMD5cbiAgRmlsZSBcIi9Vc2Vycy9reWxla2luZy9EZXZlbG9wZXIvcGFja2FnZXMvdGFpbC1qc29ubC8udmVudi9saWIvcHl0aG9uMy4xMS9zaXRlLXBhY2thZ2VzL2RvaXQvbG9hZGVyLnB5XCIsIGxpbmUgOTYsIGluIGdldF9tb2R1bGVcbiAgICByZXR1cm4gaW1wb3J0bGliLmltcG9ydF9tb2R1bGUob3MucGF0aC5zcGxpdGV4dChmaWxlX25hbWUpWzBdKVxuICAgICAgICAgICDilIIgICAgICAgICDilIIgICAgICAgICAgICAg4pSCICDilIIgICAg4pSCICAgICAgICDilJQgJ2RvZG8ucHknXG4gICAgICAgICAgIOKUgiAgICAgICAgIOKUgiAgICAgICAgICAgICDilIIgIOKUgiAgICDilJQgPGZ1bmN0aW9uIHNwbGl0ZXh0IGF0IDB4MTAyZDBjZWEwPlxuICAgICAgICAgICDilIIgICAgICAgICDilIIgICAgICAgICAgICAg4pSCICDilJQgPG1vZHVsZSAncG9zaXhwYXRoJyAoZnJvemVuKT5cbiAgICAgICAgICAg4pSCICAgICAgICAg4pSCICAgICAgICAgICAgIOKUlCA8bW9kdWxlICdvcycgKGZyb3plbik+XG4gICAgICAgICAgIOKUgiAgICAgICAgIOKUlCA8ZnVuY3Rpb24gaW1wb3J0X21vZHVsZSBhdCAweDEwMmYxY2MyMD5cbiAgICAgICAgICAg4pSUIDxtb2R1bGUgJ2ltcG9ydGxpYicgZnJvbSAnL29wdC9ob21lYnJldy9DZWxsYXIvcHl0aG9uQDMuMTEvMy4xMS4xL0ZyYW1ld29ya3MvUHl0aG9uLmZyYW1ld29yay9WZXJzaW9ucy8zLjExL2xpYi9weXRob24zLjExL2ltLi4uXG5cbiAgRmlsZSBcIi9vcHQvaG9tZWJyZXcvQ2VsbGFyL3B5dGhvbkAzLjExLzMuMTEuMS9GcmFtZXdvcmtzL1B5dGhvbi5mcmFtZXdvcmsvVmVyc2lvbnMvMy4xMS9saWIvcHl0aG9uMy4xMS9pbXBvcnRsaWIvX19pbml0X18ucHlcIiwgbGluZSAxMjYsIGluIGltcG9ydF9tb2R1bGVcbiAgICByZXR1cm4gX2Jvb3RzdHJhcC5fZ2NkX2ltcG9ydChuYW1lW2xldmVsOl0sIHBhY2thZ2UsIGxldmVsKVxuICAgICAgICAgICDilIIgICAgICAgICAg4pSCICAgICAgICAgICDilIIgICAg4pSCICAgICAgICDilIIgICAgICAgIOKUlCAwXG4gICAgICAgICAgIOKUgiAgICAgICAgICDilIIgICAgICAgICAgIOKUgiAgICDilIIgICAgICAgIOKUlCBOb25lXG4gICAgICAgICAgIOKUgiAgICAgICAgICDilIIgICAgICAgICAgIOKUgiAgICDilJQgMFxuICAgICAgICAgICDilIIgICAgICAgICAg4pSCICAgICAgICAgICDilJQgJ2RvZG8nXG4gICAgICAgICAgIOKUgiAgICAgICAgICDilJQgPGZ1bmN0aW9uIF9nY2RfaW1wb3J0IGF0IDB4MTAyYzUzZDgwPlxuICAgICAgICAgICDilJQgPG1vZHVsZSAnX2Zyb3plbl9pbXBvcnRsaWInIChmcm96ZW4pPlxuXG4gIEZpbGUgXCI8ZnJvemVuIGltcG9ydGxpYi5fYm9vdHN0cmFwPlwiLCBsaW5lIDEyMDYsIGluIF9nY2RfaW1wb3J0XG4gIEZpbGUgXCI8ZnJvemVuIGltcG9ydGxpYi5fYm9vdHN0cmFwPlwiLCBsaW5lIDExNzgsIGluIF9maW5kX2FuZF9sb2FkXG4gIEZpbGUgXCI8ZnJvemVuIGltcG9ydGxpYi5fYm9vdHN0cmFwPlwiLCBsaW5lIDExNDksIGluIF9maW5kX2FuZF9sb2FkX3VubG9ja2VkXG4gIEZpbGUgXCI8ZnJvemVuIGltcG9ydGxpYi5fYm9vdHN0cmFwPlwiLCBsaW5lIDY5MCwgaW4gX2xvYWRfdW5sb2NrZWRcbiAgRmlsZSBcIjxmcm96ZW4gaW1wb3J0bGliLl9ib290c3RyYXBfZXh0ZXJuYWw+XCIsIGxpbmUgOTQwLCBpbiBleGVjX21vZHVsZVxuICBGaWxlIFwiPGZyb3plbiBpbXBvcnRsaWIuX2Jvb3RzdHJhcD5cIiwgbGluZSAyNDEsIGluIF9jYWxsX3dpdGhfZnJhbWVzX3JlbW92ZWRcblxuPiBGaWxlIFwiL1VzZXJzL2t5bGVraW5nL0RldmVsb3Blci9wYWNrYWdlcy90YWlsLWpzb25sL2RvZG8ucHlcIiwgbGluZSAzNiwgaW4gPG1vZHVsZT5cbiAgICAxIC8vIDBcblxuWmVyb0RpdmlzaW9uRXJyb3I6IGludGVnZXIgZGl2aXNpb24gb3IgbW9kdWxvIGJ5IHplcm9cbiIsICJyZWNvcmQiOiB7ImVsYXBzZWQiOiB7InJlcHIiOiAiMDowMDowMC4zNDE3NTkiLCAic2Vjb25kcyI6IDAuMzQxNzU5fSwgImV4Y2VwdGlvbiI6IHsidHlwZSI6ICJaZXJvRGl2aXNpb25FcnJvciIsICJ2YWx1ZSI6ICJpbnRlZ2VyIGRpdmlzaW9uIG9yIG1vZHVsbyBieSB6ZXJvIiwgInRyYWNlYmFjayI6IHRydWV9LCAiZXh0cmEiOiB7fSwgImZpbGUiOiB7Im5hbWUiOiAiZG9kby5weSIsICJwYXRoIjogIi9Vc2Vycy9reWxla2luZy9EZXZlbG9wZXIvcGFja2FnZXMvdGFpbC1qc29ubC9kb2RvLnB5In0sICJmdW5jdGlvbiI6ICI8bW9kdWxlPiIsICJsZXZlbCI6IHsiaWNvbiI6ICLinYwiLCAibmFtZSI6ICJFUlJPUiIsICJubyI6IDQwfSwgImxpbmUiOiAzOCwgIm1lc3NhZ2UiOiAiZXhjZXB0aW9uLWxldmVsIGxvZyIsICJtb2R1bGUiOiAiZG9kbyIsICJuYW1lIjogImRvZG8iLCAicHJvY2VzcyI6IHsiaWQiOiAxNjI2OCwgIm5hbWUiOiAiTWFpblByb2Nlc3MifSwgInRocmVhZCI6IHsiaWQiOiA4ODIxMjQ0MTYwLCAibmFtZSI6ICJNYWluVGhyZWFkIn0sICJ0aW1lIjogeyJyZXByIjogIjIwMjMtMDEtMzEgMDY6MTY6MDAuOTExNDk5LTA1OjAwIiwgInRpbWVzdGFtcCI6IDE2NzUxNjAxNjAuOTExNDk5fX19' | base64 --decode > .logs/exception-example.jsonl`  Enter  Sleep 500ms
Type `clear`  Enter
Show

Type `cat .logs/debug-example.jsonl`  Sleep 500ms  Enter  Sleep 1s
Type `` Enter
Type `cat .logs/debug-example.jsonl | tail-jsonl`  Sleep 500ms  Enter  Sleep 3s
Type `` Enter

Type `cat .logs/exception-example.jsonl`  Sleep 500ms  Enter  Sleep 1s
Type `` Enter
Type `cat .logs/exception-example.jsonl | poetry run tail-jsonl`  Sleep 500ms  Enter  Sleep 3s
