# BiasBuster

Identify and challenge bias in language wording, primarily directed at KJZZ's radio broadcast. BiasBuster provides an automated stream downloader, a SQLite database, and Python functions to output visual statistics.

Will provide a UI and option to process other broadcasts very soon.

# Current release: WIP 0.9.3

## History
- [ ] 0.9.6   TODO web ui
- [ ] 0.9.5   TODO automate mp3 downloads from cloud + process + uploads from/to cloud server
- [ ] 0.9.4   TODO adding bias_score.py from https://github.com/auroracramer/language-model-bias
- [ ] 0.9.3   WIP adding Misinformation analysis keyword sets from https://github.com/PDXBek/Misinformation
- [x] 0.9.2   updated stopwords
- [x] 0.9.1   added wordCloud from https://github.com/amueller/word_cloud/blob/main/examples/simple.py
- [x] 0.9.0   automated mp3 process with whisper-faster from https://github.com/Purfview/whisper-standalone-win

## Requirements
- getopt, sys, os, re, regex, io, time, datetime, pathlib
- json, urllib, random, sqlite3, collections, matplotlib
- rich
- wordcloud

## Acknowledgements
- rich:       https://github.com/Textualize/rich
- wordcloud:  https://github.com/amueller/word_cloud
- https://github.com/auroracramer/language-model-bias
- https://github.com/PDXBek/Misinformation
- https://github.com/Purfview/whisper-standalone-win

