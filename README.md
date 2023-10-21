# BiasBuster - WIP 0.9.3

Identify and challenge bias in language wording, primarily directed at KJZZ's radio broadcast. BiasBuster provides an automated stream downloader, a SQLite database, and Python functions to output visual statistics.

Will provide a UI and option to process other broadcasts very soon.

Comes in 2 parts: 
- Linux part for a Cloud server, to download the mp3 (bash)
- Windows part, to transcribe mp3 to text, SQLite database management, and word analysis


# Under the hood

## Linux part: kjzz.sh
Currently, this application only downloads KJZZ's broadcast, available at https://kjzz.streamguys1.com/kjzz_mp3_128

You can certainly rewrite it for Windows if you like.

### Usage
The script accepts 2 parameters:
- *start*:  starts the download according to KJZZ-schedule.json
- *stop*:   kills current download if you want to

`kjzz.sh` will download chunks of 30mn, minus the musical programs of the night (sleep). Simply schedule CRON with this one line, to get 30mn long mp3 files under ISO week number folders (week starts Monday):
`# 0,1,30,31 * * * *   root /path/BiasBuster/kjzz.sh start`

This script will create a pid lock file with its runing PID, ensuring not 2 runs at the same time. When you run the script, it will tell you if it's running or not. Example:
`./kjzz.sh`
```
                             16:23
filename=KJZZ_2023-10-20_Fri_1600-1630_All Things Considered.mp3
kjzzDownloader 1859415 is appending "KJZZ_2023-10-20_Fri_1600-1630_All Things Considered.mp3" for the next 6 mm = 374 s. stop it?
```

### KJZZ schedule: KJZZ-schedule.json
This schedule comes from their official website at https://kjzz.org/kjzz-print-schedule

The structure is pretty simple, and simply lists by hour and by Day, what the program name is:
```
{
  "00:00": {
    "Mon": "BBC World Service",
    "Tue": "Classic Jazz with Chazz Rayburn",
    "Wed": "Classic Jazz with Bryan Houston",
    "Thu": "Classic Jazz with Bryan Houston",
    "Fri": "Classic Jazz with Michele Robins",
    "Sat": "Classic Jazz with Michele Robins",
    "Sun": "BBC World Service"
  },
  ...
```

The schedule does not look like it's going to change until next year.


## Windows part 1: BiasBuster-whisper.cmd
- Transcribe the mp3 to text with Purfview/whisper-standalone-win and CUDA
The whole point of using Windows is to put this GTX 3090 to good use. Whisper-Faster is compiled and ready to use. I tried my best to compile whisper, whisper-bin-x64, whisper-cpp, but failed miserably. This project apparently requires you to install 6GB of CUDA SDK to compile on Windows.

Here is how to transcribe the mp3 downloaded:

1. Have a CUDA GPU
2. install Whisper-Faster from https://github.com/Purfview/whisper-standalone-win
3. add cuBLAS.and.cuDNN as required
4. update `BiasBuster-whisper.cmd` to point to Whisper-Faster folder
5. copy `BiasBuster-whisper.cmd` as a shortcut in the sendTo folder (access by typing `shell:sendTo`)
6. download mp3 from your Cloud server
7. right-click the folder and select BiasBuster-whisper
8. watch the magick of IA transcription

The script as it is, will produce multiple text file formats, but this project only uses `.text` extensions at the moment: pure text, no timestamps.


## Windows part 2: KJZZ-db.py
This Python script does the following:

- Load the text files into SQLite `kjzz.db`
- Exploits the data to produce statistics and graphics
  - [x] import single mp3
  - [x] import all mp3 in a folder
  - [x] query statistics on what is stored
  - [x] query words based on schedule
  - [x] generate word cloud
  - [x] generate word cloud
  - [ ] generate gender bias analysis
  - [ ] generate misinformation heatmap
  - [ ] what else?


### Usage
`python KJZZ-db.py --help`


```
usage: python KJZZ-db.py --help
       --import [ --text "KJZZ_2023-10-13_Fri_1700-1730_All Things Considered.text" | --folder folder]
       --db *db.sqlite
       --model *small medium..
       --query [ last last10 byDay byTitle chunks10 ] (show chunks) or simply "SELECT xyz from schedule"
       --pretty (apply carriage returns)
       --gettext week=41[+title="BBC Newshour"] | date=2023-10-08[+time=HH:MM] | datetime="2023-10-08 HH:MM"
       --gettext chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" (run KJZZ-db.py -q last10 first, to get some values)
         --wordCloud [--mergeRecords] [--show] (generate word cloud for gettext output)
         --stopLevel *0 1 2 (add various levels of stopwords)
         --font_path *"fonts\Quicksand-Bold.ttf"
```

### File naming convention

#### For KJZZ
Mp3 files must be named like so, in order to be matched against KJZZ-schedule.json during loading of the database:
```
KJZZ_2023-10-13_Fri_1700-1730_All Things Considered.text
     ^          ^   ^         ^                     ^
     YYYY-MM-DD Day HHMM      Program name          text (for folder import)
```

_Day_ is redundant since we have the date, but makes the chunk name convenient to interact with.


# KJZZ-db.py Usage

## Database chunks listing
`python KJZZ-db.py -q title`

Outputs how many 30mn chunks are stored, by title and by Day:
```
 db_init: 314 chunks found in kjzz.db
[
    ('All Things Considered', 'Fri', 6),
    ('All Things Considered', 'Mon', 6),
    ('All Things Considered', 'Sat', 2),
    ('All Things Considered', 'Sun', 2),
    ...
```

## Import text files in the Database
`python KJZZ-db.py --import --folder 42`

Will import every text file in the folder "42" (week 42), and will avoid chunks already present in the database.

```
  db_init: 314 chunks found in kjzz.db
    db_load: Chunk already exist: KJZZ_2023-10-16_Mon_0000-0030_BBC World Service.text
    db_load: Chunk already exist: KJZZ_2023-10-16_Mon_0030-0100_BBC World Service.text
    ...
    db_load: Chunk added: KJZZ_2023-10-18_Wed_1030-1100_Here and Now.text
    db_load: Chunk added: KJZZ_2023-10-18_Wed_1100-1130_Here and Now.text
    ...
Loading... ---------------------------------------- 100% 0:00:00
  db_load: done loading 53/146 files
```

## List the last chunks loaded
`python KJZZ-db.py --query chunks10 -pretty`

Adding _pretty_ will flatten the results as text:

```
  db_init: 367 chunks found in kjzz.db
"KJZZ_2023-10-19_Thu_1930-2000_Fresh Air"
"KJZZ_2023-10-19_Thu_1900-1930_Fresh Air"
"KJZZ_2023-10-19_Thu_1830-1900_BBC World Business Report"
"KJZZ_2023-10-19_Thu_1800-1830_Marketplace"
"KJZZ_2023-10-19_Thu_1730-1800_All Things Considered"
"KJZZ_2023-10-19_Thu_1700-1730_All Things Considered"
"KJZZ_2023-10-19_Thu_1630-1700_All Things Considered"
"KJZZ_2023-10-19_Thu_1600-1630_All Things Considered"
"KJZZ_2023-10-19_Thu_1530-1600_All Things Considered"
"KJZZ_2023-10-19_Thu_1500-1530_All Things Considered"
```

## gettext
validKeys = they will be used as parameters for the SQL query:
- date
- datetime
- week
- Day
- time
- title
- chunk

You can also combine the keys with *+*, examples:
- ALL of BBC Newshour for week 41: `--gettext week=41+title="BBC Newshour"`
- ALL programs for a specific day [and time]: `--gettext date=2023-10-08[+time=HH:MM]`
- Specific date and time (30mn chunk): `--gettext datetime="2023-10-08 HH:MM"`


### Get the text for a particular chunk
`python KJZZ-db.py --gettext chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -p`


### Get the text for a particular program, ALL dates
`python KJZZ-db.py --gettext title="All Things Considered" -p`


### Generate a word Cloud for a particular chunk of program
`python KJZZ-db.py -g chunk="KJZZ_2023-10-19_Thu_1500-1530_All Things Considered" -v --wordCloud`

Verbose outpout:
```
wordCloud:     True
localSqlDb kjzz.db passed
  db_init kjzz.db
    cursor: 1 records
  db_init: 367 chunks found in kjzz.db
  gettext: SELECT text from schedule where 1=1 and start = '2023-10-19 15:00:00.000'
    cursor: 1 records
  gettext: image 1
    genWordCloud: most 10 common words before: [('the', 208), ('to', 142), ('a', 114), ('of', 110), ('in', 91), ('and', 89), ('that', 73), ('is',
70), ('this', 58), ('on', 49)]
    genWordCloud: most 10 common words after:  [('s', 68), ('you', 41), ('I', 37), ('are', 34), ('from', 32), ('they', 32), ('have', 24), ('like',
24), ('was', 23), ('so', 23)]
    genWordCloud: 4952 words - 195 stopWords == 3694 total words (1258 words removed)
    genWordCloud: stopWords = {"we're", 'nor', 'start=2023-10-19', 'they', "doesn't", 'we', 'on', 'me', 'can', 'out', 'get', "she's", 'about',
'few', 'once', "we'd", "you'd", 'of', "here's", 'is', 'www', 'but', "he'd", 'to', 'both', 'k', 'below', 'was', 'themselves', 'could', 'up',
'while', 'where', 'other', "shouldn't", 'like', 'or', 'same', 'what', 'myself', "it's", 'our', 'how', 'doing', 'her', 'ours', 'such', 'further',
'my', "there's", "couldn't", "they've", 'only', "i'll", 'it', 'then', 'therefore', 'else', 'which', 'after', 'just', 'for', 'be', 'very', 'at',
'are', 'since', 'being', 'r', 'against', 'too', 'should', 'having', 'were', 'in', 'them', "you're", 'yours', 'KJZZ', 'into', 'however', 'if',
'through', "why's", 'all', 'himself', 'more', "you've", 'otherwise', 'did', "she'd", "what's", "she'll", 'who', 'own', "wasn't", 'during',
"you'll", 'their', 'here', "won't", 'those', 'you', "who's", "didn't", "where's", 'has', "shan't", 'no', 'not', "can't", "hadn't", 'http',
'again', "don't", 'i', "aren't", 'ever', "let's", 'hence', 'with', 'until', 'whom', 'why', 'had', 'been', 'there', 'under', "we'll", "i'm",
'yourselves', 'am', "i'd", 'above', 'as', 'over', 'this', 'some', 'each', 'itself', 'from', 'between', 'that', "when's", "they're", 'off', 'any',
'an', 'the', "isn't", '15:00', 'and', "i've", 'his', "hasn't", 'most', "he'll", 'a', 'when', 'these', 'hers', 'by', "weren't", 'com', 'also',
'its', 'your', 'cannot', "haven't", "wouldn't", 'before', "they'll", 'than', 'yourself', 'ourselves', "he's", 'him', "how's", "they'd", 'ought',
"that's", 'because', 'do', 'herself', 'down', 'shall', 'she', 'he', 'does', "we've", 'so', 'would', 'have', "mustn't", 'theirs'}
    genWordCloud: file = "KJZZ start=2023-10-19 1500 words=4952 max=4000 scale=0.png"
```

wordCloud generated:
!["KJZZ start=2023-10-19 1500 words=4952 max=4000 scale=0.png"](URL "assets/KJZZ start=2023-10-19 1500 words=4952 max=4000 scale=0.png")


# Roadmap
- [ ] 0.9.7   TODO separate KJZZ into its own table to add other broadcasters
- [ ] 0.9.6   TODO web ui
- [ ] 0.9.5   TODO automate mp3 downloads from cloud + process + uploads from/to cloud server
- [ ] 0.9.4   TODO adding bias_score.py from https://github.com/auroracramer/language-model-bias
- [ ] 0.9.3   WIP adding Misinformation heatmap from https://github.com/PDXBek/Misinformation
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

