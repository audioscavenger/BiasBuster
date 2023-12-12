# BiasBuster
# author:  AudioscavengeR
# license: GPLv2
# version: 0.9.11 WIP

# BUG: jpeg produced by plt.savefig have a wide border

# Object: Identify and challenge bias in language wording, primarily directed at KJZZ's radio broadcast.
# BiasBuster provides an automated stream downloader, a SQLite database, and Python functions to output visual statistics.
# BiasBuster will produce:
# - CUDA word transcription from any audio files, based on Whisper-Faster
# - Words cloud, based on amueller/word_cloud
# - Gender bias statistics, based on auroracramer/language-model-bias
# - Misinformation analysis heatmap, based on PDXBek/Misinformation


# https://kjzz.org/kjzz-print-schedule

# python KJZZ-db.py -i -f kjzz\44
# python KJZZ-db.py -i -f kjzz\45
# python KJZZ-db.py -q title
# python KJZZ-db.py -q chunkLast10 -p
# python KJZZ-db.py -g chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v --wordCloud
# python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
# python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
# python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
# python KJZZ-db.py -g title="BBC Newshour" -v --wordCloud
# python KJZZ-db.py -g title="BBC World Business Report" -v --wordCloud
# python KJZZ-db.py -g title="BBC World Service" -v --wordCloud
# python KJZZ-db.py -g title="Fresh Air" -v --wordCloud
# python KJZZ-db.py -g title="Here and Now" -v --wordCloud
# python KJZZ-db.py -g title="Marketplace" -v --wordCloud
# python KJZZ-db.py -g title="Morning Edition" -v --wordCloud
# python KJZZ-db.py -g title="The Show" -v --wordCloud
# python KJZZ-db.py -g week=42+Day=Mon+title="The Show" -v --wordCloud --stopLevel 3
# python KJZZ-db.py -g week=42+Day=Mon+title="All Things Considered" --wordCloud --stopLevel 3 --show
# python KJZZ-db.py -g week=42 --wordCloud --stopLevel 3 --show --max_words=10000
# python KJZZ-db.py -g week=43 --wordCloud --stopLevel 3 --show --max_words=10000
# python KJZZ-db.py -g week=44 --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
# python KJZZ-db.py -g week=43+title="TED Radio Hour" --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
#   example: week=42+title="Freakonomics"+Day=Sun is about men/women
# python KJZZ-db.py -g week=42+title="Freakonomics"+Day=Sun --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
# for /l %a in (40,1,45) DO python KJZZ-db.py -g week=%a+title="TED Radio Hour" --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
# python KJZZ-db.py -g week=42+title="Freakonomics"+Day=Sun --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt

# python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --graph pie --show
# python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --noMerge   --show
# python KJZZ-db.py --html 42 --byChunk
# python KJZZ-db.py --rebuildThumbnails 41
# for /l %a in (40,1,47) DO python KJZZ-db.py --html %a --autoGenerate --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt


# TODO: enable closed-captions by default: nothing works, asked on stackoverflow
# similar question: https://stackoverflow.com/questions/17247931/video-js-how-do-i-make-subtitle-visible-by-default
# my question: https://stackoverflow.com/questions/77581173/how-to-enable-closed-captions-by-default-with-openplayerjs-video-js

# TODO: improve file read fd with list = set(map(str.strip, open(os.path.join(inputFolder, fileName)).readlines()))
# TODO: somehow find way to always include --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
# TODO: add --force to regenerate existing pictures
# TODO: handle same program at differnt time of the day such as Sat: BBC World Service morning and evening - currently we can only generate one same wordCloud for both
# TODO: heatMap: do we keep stopWords or not, brfore the counting occurs?
# TODO: https://github.com/auroracramer/language-model-bias
# TODO: export all configuration into external json files or yaml
# TODO: explore stopWords from https://github.com/taikuukaits/SimpleWordlists/
# TODO: analyse gender bias
# TODO: analyse language bias
# egrep -i "trans[gsv]|\bgay\b|\blesb|\bbisex|\btransg|\bqueer|gender|LGBT" *text
# egrep -i "diversity|equity|inclusion" *text




import getopt, sys, os, re, regex, io, inspect, string, copy
import glob, time, datetime, json, urllib, random, sqlite3
from dateutil import parser
from pathlib import Path
from collections import Counter

# 3rd party modules:
# https://github.com/Textualize/rich
from rich import print
from rich.progress import track, Progress

# we do not preload this bunch unless we need them:
# -------------------------------------------------
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from   matplotlib import style
# from   matplotlib.patches import Rectangle
# import seaborn
# import pngquant
# pngquant.config(min_quality=1, max_quality=20, speed=1, ndeep=2)
# -------------------------------------------------


# def root():
  # parent()
# def parent():
  # child()
# def child(stack=''):
  # for i in reversed(range(0, len(inspect.stack())-1)): stack += "%s: " %(inspect.stack()[i][3])
  # print("%s: " %(stack))


# # example of progress bar:
# with Progress() as progress:
  # task = progress.add_task("twiddling thumbs", total=10)
  # inputFiles = [1,2,3,4,5,6,7,8,9,0]
  # for inputFile in inputFiles:
    # progress.console.print(f"Working on job #{inputFile}")
    # time.sleep(0.2)
    # progress.advance(task)
# exit()

verbose = 1
progress = ""

importChunks = False
inputFolder = None
inputFiles = []
inputJsonFile = None
inputTextFile = None
localSqlDb = Path("kjzz.db")
# the db connection is global
conn = None

model = "small"
sqlQuery = None
pretty = False
wordCloud = False
misInformation = False
gettext = None
listTitleWords2Exclude = ["Jazz", "Blues"]
gettextKeys = ["date", "datetime", "week", "Day", "time", "title", "chunk"]
gettextDict = {}
mergeRecords = True
removeStopwords = True
showPicture = False
inputStopWords = []
outputFolder = Path("./kjzz")
dataFolder = Path("./data")
thesaurusFolder = Path("./data/SimpleWordlists")
graphs = []   # bar pie line
weekNumber = 0
jsonScheduleFile = os.path.realpath("kjzz/KJZZ-schedule.json")
byChunk = False
printOut = False
listLevel = []
silent = False
autoGenerate = False
dryRun = False
noPics = False
missingPic = "../missingPic.png"
missingCloud = "../missingCloud.png"
voidPic = "../1x1.png"
rebuildThumbnail = False
usePngquant = True
useJpeg = False
jpegQuality = 50
force = False
# when uncertainty/sourcing >= BSoMeterTrigger then highlight it
BSoMeterTrigger = 0.9
BSoMeterLevel2 = 0.93
defaultGraphs = ["bar", "pie"]
withSynonyms = True
minChunkSize = 20000

dictHeatMapBlank = { 
  "explanatory":{"words":set(),"heatCount":0,"heat":None}, 
  "retractors":{"words":set(),"heatCount":0,"heat":None}, 
  "sourcing":{"words":set(),"heatCount":0,"heat":None}, 
  "uncertainty":{"words":set(),"heatCount":0,"heat":None}, 
}

# busybox sed -E "s/^.{,3}$//g" stopWords.ranks.nl.txt | busybox sort | busybox uniq >stopWords.ranks.nl.txt 
# wordcloud internal STOPWORDS: https://github.com/amueller/word_cloud/blob/main/wordcloud/stopwords
# https://www.ranks.nl/stopwords
# https://gist.github.com/sebleier/554280
# https://github.com/taikuukaits/SimpleWordlists/blob/master/Wordlist-Adjectives-All.txt
# wget https://raw.githubusercontent.com/taikuukaits/SimpleWordlists/master/Wordlist-Adjectives-All.txt -OstopWords.Wordlist-Adjectives-All.txt

stopLevel = 3
# after merging 0+1 we get this:
# stopwordsDict = {
# 0: ['up', 'ever', 'yourself', 'therefore', 'cannot', 'could', 'new', "they've", 'theirs', "who's", 'u', 'an', 'am', 'get', 're', 'where', 'herself', 'same', 'was', "you'd", 'www', 'some', 'through', 'each', 'himself', 'once', 'me', 'have', 'our', 'this', 'or', "i'm", 'they', "hasn't", 'which', 'why', 'to', "how's", 'can', 'com', 'we', 'did', 'yours', 'the', "we're", 'more', 'shall', 'about', 'are', 'so', "they're", "he'd", 'otherwise', 'below', 'else', 'further', 'has', 'most', 'ours', 'ourselves', "why's", 'a', 'at', "we'd", 'between', "isn't", 'that', 'one', 'since', "doesn't", 'her', 'into', 'k', "couldn't", 'before', "she'd", "wasn't", 'it', "don't", 'during', 'only', 'hers', "when's", "shouldn't", "she's", 'in', 'my', 'no', 'however', 'r', "they'll", 'above', 'if', 'he', 'of', 'how', 'over', 'say', 'whom', "we've", "here's", 'been', "hadn't", 's', 'be', 'these', 'own', 'both', 'doing', 'itself', 'but', 'against', 'ought', 'http', 'nor', "weren't", "he's", 'does', 'i', 'and', "what's", "wouldn't", 'myself', 'just', 'out', "they'd", 'on', 'than', 'hence', 'themselves', 'then', 'very', "we'll", 'she', "it's", "you'll", 'its', 'is', "let's", 'were', "won't", 'what', 'by', "that's", 'again', 'had', 'too', "mustn't", "i've", "there's", 'as', "she'll", 'few', 'being', 'when', "aren't", 'should', "shan't", 'all', 'under', 'your', 'here', 'down', 'with', 'also', 'after', "you're", 'like', 'you', "where's", 'not', 'any', 'him', 'until', "you've", 'says', "didn't", 'such', "i'd", "i'll", 'them', 'do', 'while', "haven't", 'there', 'their', 'who', 'because', "he'll", "can't", 'from', 'having', 'for', 'off', 'other', 'would', 'those', 'yourselves', 'his'],
# }

# build from https://github.com/amueller/word_cloud/blob/master/wordcloud/wordcloud.py
wordCloudDict = {
  "max_words": {
    "input": True, 
    "default": 200, 
    "value": 1000, 
    "usage": "int (default=1000)\n               The maximum number of words in the Cloud.", 
  },
  "width": {
    "input": True, 
    "default": 400, 
    "value": 2000, 
    "usage": "int (default=2000)\n               Width of the canvas.", 
  },
  "height": {
    "input": True, 
    "default": 200, 
    "value": 1000, 
    "usage": "int (default=1000)\n               Height of the canvas.", 
  },
  "min_word_length": {
    "input": True, 
    "default": 0, 
    "value": 3, 
    "usage": "int, default=3\n               Minimum number of letters a word must have to be included.", 
  },
  "min_font_size": {
    "input": True, 
    "default": 4, 
    "value": 4, 
    "usage": "int (default=4)\n               Smallest font size to use. Will stop when there is no more room in this size.", 
  },
  "max_font_size": {
    "input": True, 
    "default": 0, 
    "value": 400, 
    "usage": " int or None (default=400)\n               Maximum font size for the largest word. If None, height of the image is used.", 
  },
  "scale": {
    "input": True, 
    "default": 1.0, 
    "value": 1.0, 
    "usage": "float (default=1.0)\n               Scaling between computation and drawing. For large word-cloud images,\n               using scale instead of larger canvas size is significantly faster, but\n               might lead to a coarser fit for the words.", 
  },
  "relative_scaling": {
    "input": True, 
    "default": 0.0, 
    "value": 'auto', 
    "usage": "float (default='auto')\n               Importance of relative word frequencies for font-size.  With\n               relative_scaling=0, only word-ranks are considered.  With\n               relative_scaling=1, a word that is twice as frequent will have twice\n               the size.  If you want to consider the word frequencies and not only\n               their rank, relative_scaling around .5 often looks good.\n               If 'auto' it will be set to 0.5 unless repeat is true, in which\n               case it will be set to 0.", 
  },
  "background_color": {
    "input": True, 
    "default": 'black', 
    "value": 'white', 
    "usage": "color value (default='white')\n               Background color for the word cloud image.", 
  },
  "normalize_plurals": {
    "input": True, 
    "default": True, 
    "value": True, 
    "usage": "bool, default=True\n               Whether to remove trailing 's' from words. If True and a word\n               appears with and without a trailing 's', the one with trailing 's'\n               is removed and its counts are added to the version without\n               trailing 's' -- unless the word ends with 'ss'. Ignored if using\n               generate_from_frequencies.", 
  },
  "inputStopWordsFiles": {
    "input": True, 
    "default": [], 
    "value": [], 
    "usage": "file, default=None\n               Text file containing one stopWord per line.\n               You can pass --inputStopWordsFiles multiple times.", 
  },
  "inputStopWords": {
    "input": False, 
    "default": [], 
    "value": [], 
    "usage": "list, default=[]\n               Consolidated list of stopWords from inputStopWordsFiles.", 
  },
  "font_path": {
    "input": True, 
    "default": None, 
    "value": "fonts\\Quicksand-Bold.ttf", 
    "usage": "str, default='fonts\\Quicksand-Bold.ttf'\n               Font path to the font that will be used (OTF or TTF).", 
  },
  "collocation_threshold": {
    "input": True, 
    "default": 30, 
    "value": 30, 
    "usage": "int, default=30\n               Bigrams must have a Dunning likelihood collocation score greater than this\n               parameter to be counted as bigrams. Default of 30 is arbitrary.\n               See Manning, C.D., Manning, C.D. and Schütze, H., 1999. Foundations of\n               Statistical Natural Language Processing. MIT press, p. 162\n               https://nlp.stanford.edu/fsnlp/promo/colloc.pdf#page=22", 
  },
}

sqlListLast10text = """ SELECT text from schedule LIMIT 10 """
sqlLastText       = """ SELECT text from schedule LIMIT 1 """
sqlFirstText      = """ SELECT text from schedule ORDER BY start DESC LIMIT 1 """

# BUG: what we want is order by iso week day = %u but only %w (Sunday first) works
sqlCountsByDay    = """ SELECT Day, title, count(start)
          from schedule 
          GROUP BY Day, title
          ORDER BY strftime('%w',start)
          """
# [
  # ('Fri', 'All Things Considered', 5),
  # ('Fri', 'BBC Newshour', 2),
  # ('Fri', 'BBC World Service', 4),
  # ('Fri', 'Here and Now', 4),
  # ('Fri', 'Morning Edition', 12),
  # ('Fri', 'Science Friday', 2),
  # ('Fri', 'The Show', 2),

sqlTitles = """ SELECT title
          from schedule 
          GROUP BY title
          ORDER BY title, strftime('%w',start)
          """

sqlCountsByTitle = """ SELECT title, Day, count(title)
          from schedule 
          GROUP BY title, Day
          ORDER BY title, strftime('%w',start)
          """
# [
  # ('All Things Considered', 'Fri', 5),
  # ('All Things Considered', 'Thu', 6),
  # ('All Things Considered', 'Tue', 1),
  # ('All Things Considered', 'Wed', 6),
  # ('BBC Newshour', 'Fri', 2),

# spit out chunk names, useful list what's available
# KJZZ_2023-10-09_Mon_0000-0030_BBC World Service
# https://www.sqlite.org/lang_datefunc.html
# https://www.sqlshack.com/sql-convert-date-functions-and-formats/
# python KJZZ-db.py -q chunkLast10 -p
# %w 		day of week 0-6 with Sunday==0 but we want Mon Tue etc
sqlListChunksLast10 = """ SELECT 'KJZZ_' || strftime('%Y-%m-%d_%w_%H%M-',start) || strftime('%H%M_',stop) || title
          from schedule 
          ORDER BY start DESC
          LIMIT 10
          """
# [
  # ('KJZZ_2023-10-13_41_1700-1730_All Things Considered',),
  # ('KJZZ_2023-10-13_41_1630-1700_All Things Considered',),
  # ('KJZZ_2023-10-13_41_1600-1630_All Things Considered',),
  # ('KJZZ_2023-10-13_41_1530-1600_All Things Considered',),
  # ('KJZZ_2023-10-13_41_1500-1530_All Things Considered',),
  # ('KJZZ_2023-10-13_41_1330-1400_BBC Newshour',),

sqlCountsByWord = """ SELECT title, Day, count(start)
          from schedule 
          GROUP BY title, Day
          ORDER BY title
          """
# [
  # ('All Things Considered', 'Fri', 5), <- insert word count after the 5
  # ('All Things Considered', 'Thu', 6),
  # ('All Things Considered', 'Tue', 1),
  # ('All Things Considered', 'Wed', 6),
  # ('BBC Newshour', 'Fri', 2),

# https://www.datacamp.com/tutorial/wordcloud-python
# https://github.com/amueller/word_cloud/blob/main/examples/simple.py


class TimeDict:
  def __init__(self, dateTime):
  # dateTime = YYYY-MM-DD HH:MM:SS.SSS
    self.dateTime = dateTime
    self.split = re.split(r"[ -]", dateTime) # ['2023', '10', '09', 'HH:MM:SS.SSS']
    self.week = datetime.date(int(self.split[0]),int(self.split[1]),int(self.split[2])).isocalendar().week
    self.YYYYMMDD = dateTime[:10]
    self.Day = datetime.date(int(self.split[0]),int(self.split[1]),int(self.split[2])).strftime('%a')
    self.time = self.split[3]
    self.HHMM = self.split[3][:5]
    
# class TimeDict


class Chunk:
  def __init__(self, inputFile, model=model, loadText=True, progress=""):
    self.inputFile = Path(inputFile)
    self.model = model
    self.dirname = os.path.dirname(self.inputFile)
    self.basename = os.path.basename(self.inputFile)
    self.stem = Path(self.basename).stem
    self.ext = Path(self.basename).suffix
    self.split = re.split(r"[_-]", self.stem) # ['KJZZ', '2023', '10', '09', 'Mon', '1330', '1400', 'BBC Newshour']
    if len(self.split) != 8:
      raise ValueError("Chunk: invalid name: %s" % (self.inputFile))
    self.week = datetime.date(int(self.split[1]),int(self.split[2]),int(self.split[3])).isocalendar().week
    self.YYYYMMDD = '-'.join([self.split[1],self.split[2],self.split[3]])
    self.Day = self.split[4]
    # we want YYYY-MM-DD HH:MM:SS.SSS
    self.startHHMM = ':'.join([self.split[5][:2],self.split[5][2:]])
    self.startTime = ':'.join([self.split[5][:2],self.split[5][2:]]) + ":00.000"
    self.start = ' '.join([self.YYYYMMDD, self.startTime])
    self.stopHHMM = ':'.join([self.split[6][:2],self.split[6][2:]])
    self.stopTime = ':'.join([self.split[6][:2],self.split[6][2:]]) + ":00.000"
    self.stop = ' '.join([self.YYYYMMDD, self.stopTime])
    self.title = self.split[-1]
    
    # generally for 30mn chunks, text files are 25k on average
    if os.path.isfile(self.inputFile):
      self.size = os.path.getsize(self.inputFile)
      if self.size < minChunkSize:
        warning("%s [%.1fk] small size is sus" %(self.inputFile, self.size/1024), 0, progress)
      if loadText:
        # with open(self.inputFile, 'r') as pointer:
        with io.open(self.inputFile, mode="r", encoding="utf-8") as pointer:
          # separate sentences properly:
          text = pointer.read().replace('\n',' ')
          self.text = text.replace('. ','.\n')
          # ddebug(self.text)
    else:
      raise ValueError("Chunk: file not found: %s" % (self.inputFile))
# class Chunk


# TODO: update table for missing columns when this script is updated
# TODO: defind columns in a dict and compare to records from this command:
# pragma table_info('schedule')
  # 0	start	TEXT	0		1
  # 1	stop	TEXT	1		0
  # 2	week	INTEGER	0		0
  # 3	day	TEXT	1		0
  # 4	title	TEXT	1		0
  # 5	text	TEXT	0		0
  # 6	model	TEXT	0		0

# TODO: check indexes exist and create them if not:
# SELECT * FROM sqlite_master WHERE type= 'index' and tbl_name = 'schedule' and name = 'IFK_ScheduleStartStop';
  # index	IFK_ScheduleStartStop	schedule	13436	CREATE UNIQUE INDEX "IFK_ScheduleStartStop" ON "schedule" (
    # "start",
    # "stop"
  # )

# TEST if index is used: https://stackoverflow.com/questions/35625812/sqlite-use-autoindex-instead-my-own-index
# analyze schedule;
# explain query plan SELECT start, text from schedule where 1=1 and week = 40 and title = 'Classic Jazz with Chazz Rayburn' and Day = 'Mon';
  # 4	0	0	SEARCH TABLE schedule USING INDEX IFK_ScheduleWeekTitleDay (week=? AND title=? AND day=?)
  # yes it is!!!


# If you use the TEXT storage class to store date and time value, you need to use the ISO8601 string format as follows:
# YYYY-MM-DD HH:MM:SS.SSS
def db_init(localSqlDb):
  localSqlDb.touch()
  # localSqlDb.unlink()
  conn = sqlite3.connect(localSqlDb)
  cur = conn.cursor()
  queryScheduleTable = """
    CREATE TABLE schedule (
          start           TEXT    PRIMARY KEY
        , stop            TEXT    NOT NULL
        , week            INTEGER
        , Day             TEXT    NOT NULL
        , title           TEXT    NOT NULL
        , text            TEXT
        , model           TEXT
        , misInfo         TEXT
        );
    CREATE UNIQUE INDEX [IFK_ScheduleStartStop]    ON "schedule" ([start],[stop]);
    CREATE        INDEX [IFK_ScheduleWeekTitleDay] ON "schedule" ([week],[title],[Day]);
    """
  try:
    cur.execute(queryScheduleTable)
    info("queryScheduleTable %s: success" %(localSqlDb), 1)
  except Exception as error:
    if not str(error).find("already exists"):
      info("queryScheduleTable %s: %s" %(localSqlDb, error), 1)
    else:
      records = cursor(localSqlDb, conn, """SELECT count(start) from schedule""")
      info("%s chunks found in schedule %s" %(records[0][0], localSqlDb), 1)
  
  queryStatsTable = """
    CREATE TABLE statistics (
          week          INTEGER NOT NULL
        , Day           TEXT    NOT NULL
        , title         TEXT    NOT NULL
        , top100tuples  TEXT
        , PRIMARY KEY (week, day, title)
        );
    """
  try:
    cur.execute(queryStatsTable)
    info("queryStatsTable %s: success" %(localSqlDb), 1)
  except Exception as error:
    if not str(error).find("already exists"):
      info("queryStatsTable %s: %s" %(localSqlDb, error), 1)
    else:
      records = cursor(localSqlDb, conn, """SELECT count(*) from statistics""")
      info("%s lines found in statistics %s" %(records[0][0], localSqlDb), 1)
  
  return conn
  #
#

# with Progress() as progress:
  # task = progress.add_task("twiddling thumbs", total=10)
  # inputFiles = [1,2,3,4,5,6,7,8,9,0]
  # for inputFile in inputFiles:
    # progress.console.print(f"Working on job #{inputFile}")
    # time.sleep(0.2)
    # progress.advance(task)

def db_update(table, column, value, textConditions, localSqlDb, conn, commit, progress=""):
  # db_update('schedule', 'misInfo', str(misInfo), textConditions, localSqlDb, conn)
  if not conn:
    conn = sqlite3.connect(localSqlDb)

  # if isinstance(value,str):
  sqlText = """ UPDATE ${table} SET ${column}='${value}' where 1=1 ${textConditions}; """
  sql = string.Template((sqlText)).substitute(dict(table=table, column=column, value=value, textConditions=textConditions))
  info(sql, 3, progress)
  
  # records is always [] for an update
  records = cursor(localSqlDb, conn, sql)
  if commit and not dryRun: conn.commit()
  
# db_update


def db_load(inputFiles, localSqlDb, conn, model, commit, progress=""):
  importedFiles = []
  if inputFiles:
    info("%s files found" %(len(inputFiles)), 1)
  if not conn:
    conn = sqlite3.connect(localSqlDb)
  
  # tentative to use BEGIN+COMMIT to speed up loading at the expense of memory
  # sqlLoad = """ BEGIN; """
  
  with Progress() as progress:
    task = progress.add_task("Loading inputFiles", total=len(inputFiles))
    # KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.text
    for inputFile in inputFiles:
      info('Chunk init:     "%s"' % (inputFile), 3, progress)
      try:
        # first we do not read the file:
        chunk = Chunk(inputFile, model, False, progress)
        # time.sleep(0.2)
      except Exception as error:
        error('Chunk error:    "%s": %s' % (chunk.basename, error), 11)
      
      # check if exist in db:
      sqlCheck = """ SELECT * from schedule where start = ?; """
      records = cursor(localSqlDb, conn, sqlCheck, (chunk.start,), progress)
      # exit()
      if len(records) == 0 or force:
        # recreate chunk and actually read the file:
        try:
          chunk = Chunk(inputFile, model, True, progress)
          info('Chunk read:     "%s" [%.1fk]' % (chunk.basename, chunk.size/1024), 3, progress)
          # time.sleep(0.2)
        except Exception as error:
          error('Chunk error:    "%s": %s' % (chunk.basename, error), 11)
        
        # load Chunk in db:
        if len(records) == 0:
          sqlLoad = """ INSERT INTO schedule(start, stop , week, Day, title, text, model) VALUES(?,?,?,?,?,?,?); """
          records = cursor(localSqlDb, conn, sqlLoad, (chunk.start, chunk.stop , chunk.week, chunk.Day, chunk.title, chunk.text, chunk.model), progress)
        else:
          # you can only use ? in this case: VALUES(?,?,?,?,?,?,?) - not in a WHERE clause or anything else
          sqlUpdate = """ UPDATE schedule set (text, model) = (?,?) WHERE start = '%s'; """ %(chunk.start)
          records = cursor(localSqlDb, conn, sqlUpdate, (chunk.text, chunk.model), progress)
        
        importedFiles += [inputFile]
        info('Chunk imported: "%s" [%.1fk]' % (chunk.basename, chunk.size/1024), 2, progress)
      else:
        info('Chunk exist:    "%s"' % (chunk.basename), 2, progress)
      progress.advance(task)
  
  # BEGIN+COMMIT cannot work like this unfortunately: You can only execute one statement at a time.
  # records = cursor(localSqlDb, conn, sqlLoad, None, progress)
  
  if commit and not dryRun: conn.commit()
  info("Done loading %s/%s files" %(len(importedFiles), len(inputFiles)), 1, progress)
#


def cursor(localSqlDb, conn, sql, data=None, progress=""):
  if not conn:
    conn = sqlite3.connect(localSqlDb)
  cur = conn.cursor()
  records = []
  try:
    if data is not None:
      info("cur.execute(%s) ... %s ..." %(sql, data[0]), 4, progress)
      # ddebug(sql, data)
      cur.execute(sql, data)
    else:
      info("cur.execute(%s) ..." %(sql), 4, progress)
      cur.execute(sql)
    records = cur.fetchall()
    info("%s records" %(len(records)), 4, progress)
  except Exception as error:
    error("cur.execute(%s) ..." %(sql))
    error("%s" %(error))
  return records
#


def sqlQueryPrintExec(sqlQuery, pretty=pretty):
  info("sqlQuery: %s" % (sqlQuery), 2)
  records = cursor(localSqlDb, conn, sqlQuery)
  # SQLite: %w = day of week 0-6 with Sunday==0
  # But we want Mon Tue etc so we replace text in each tuple.
  # Oh yeah, sqlite3 fetchall returns a list of tuples.
  # Each record is a tuple: ('KJZZ_2023-10-13_5_1630-1700_All Things Considered',),
  if sqlQuery.find('_%w_') > -1:
    # replaceNum2Days will output the same input format: str or tuple: 0->Sun 1->Mon etc
    # What we should do is grab the recursive replace function I wrote 10 years ago, pfff where is it
    records = [replaceNum2Days(record) for record in records]
    # records[0] = map(lambda x: str.replace(x, "[br]", "<br/>"), records[0])
  if pretty:
    for record in records:
      print(('"%s"') %(record))
  else:
    print(records)
  #
  return records
#

# # this works only with full key replacement
# subs = { "Houston": "HOU", "L.A. Clippers": "LAC", }
# my_lst = ['LAC', 'HOU', '03/03 06:11 PM', '2.13', '1.80', 'LAC']
# my_lst[:] = map(dict(zip(subs.values(), subs)).get, my_lst[:])
# print (my_lst)

# # just started modifying but this is impossible
# invertWeekDays = { "Sun": "_0_", "Mon": "_1_", "Tue": "2", "Wed": "3", "Thu": "4", "Fri": "5", "Sat": "6", }
# my_lst = ['zzz_0_xxx', 'yy_1_33', '03/03 06:11 PM', '2.13', '1.80', '03/03 03:42 PM']
# my_lst = map(dict(zip(invertWeekDays.values(), invertWeekDays)).get, my_lst)
# print(my_lst)

def replaceNum2Days(record):
  # crap multi replace function but it's cheap
  if isinstance(record,str):
    newRecord = record
  else:
    newRecord = record[0]
  newRecord = newRecord.replace('_0_','_Sun_')
  newRecord = newRecord.replace('_1_','_Mon_')
  newRecord = newRecord.replace('_2_','_Tue_')
  newRecord = newRecord.replace('_3_','_Wed_')
  newRecord = newRecord.replace('_4_','_Thu_')
  newRecord = newRecord.replace('_5_','_Fri_')
  newRecord = newRecord.replace('_6_','_Sat_')
  if isinstance(record,str):
    return newRecord
  else:
    return (newRecord,)
#


def checkChunk(getTextDict, progress=""):
  # gettextDict = {'start': '%Y-%m-%d %H:%M'}
  # gettextDict = {'week': '40', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
  sqlGettext = "SELECT count(*) from schedule where 1=1"
  
  # build the actual query
  for key in gettextDict.keys():
    # build the SQL query:
    sqlGettext += (" and %s = '%s'" % (key, gettextDict[key]))
    
    # reformat start time for the fileName: chunk has been build if the key is "chunk"
    if key == "start":
      gettextDict[key] = parser.parse(gettextDict[key]).strftime("%Y-%m-%d %H:%M")
    
  info("sqlGettext: %s" %(sqlGettext), 3, progress)
  
  records = cursor(localSqlDb, conn, sqlGettext)
  if len(records) == 0:
    info("0 records for %s" %(gettextDict), 4, progress)
  
  return records[0][0]
# gettext



# the db has:   start stop week day title text model misInfo
# and we want:  start stop KJZZ_YYYY-mm-DD_Ddd_HHMM-HHMM_Title misInfo
def getChunks(getTextDict, withText=False, progress=""):
  # gettextDict = {'start': '%Y-%m-%d %H:%M'}
  # gettextDict = {'week': '40', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
  
  selectText = ''
  if withText: selectText = ', text'

  textConditions = ''
  for column, value in gettextDict.items():
    textConditions += " and %s='%s'" %(column, value)
  
          # strftime('%%H:%%M',start)
        # , strftime('%%H:%%M',stop)
  # let's return actual times instead, it's more useful
  sqlListChunks = """ SELECT 
          start
        , stop
        , 'KJZZ_' || strftime('%%Y-%%m-%%d_',start) || Day || strftime('_%%H%%M-',start) || strftime('%%H%%M_',stop) || title
        , misInfo
        %s
          from schedule 
          where 1=1
          %s
          ORDER BY start ASC;
          """ %(selectText, textConditions)
  
  info("sqlListChunks: %s" %(sqlListChunks), 4, progress)
  
  records = cursor(localSqlDb, conn, sqlListChunks)
  if len(records) == 0:
    info("0 records for %s" %(gettextDict), 3, progress)
  
  return records
  # records = [
    # ('2023-10-14 01:00.000', '2023-10-14 01:30.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]'),
    # ('2023-10-14 01:30.000', '2023-10-14 02:00.000', 'KJZZ_2023-10-14_Sat_0130-0200_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...'),
    # ...
# gettext


def printOutGetText(records, mergeRecords, pretty, dryRun):
  if mergeRecords:
    mergedText = ''
    for record in records: mergedText += record[1]
    if pretty:
      print(('"%s"') %(mergedText))
    else:
      print(mergedText)
  else:
    for record in records:
      if pretty:
        print(('"%s"') %(record[1]))
      else:
        print(record)
#



def genWordClouds(records, wordCloudTitle, mergeRecords, showPicture, wordCloudDict, outputFolder=outputFolder, dryRun=False, progress=""):
  # gettext = "week=43+title=Classic Jazz with Chazz Rayburn+Day=Mon"
  # gettextDict = {'week': '43', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
  # records = (('2023-10-14 01:00.000', '2023-10-14 01:30.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...'),..)
  # wordCloudTitle = "KJZZ week=43 title=BBC World Service Day=Sat"
  
  if len(records) == 0: return []
  genWordCloudDicts = []
  mergedText = ''
  
  if mergeRecords:
    for record in records: mergedText += record[4]
    genWordCloudDicts.append(genWordCloud(mergedText, wordCloudTitle, removeStopwords, stopLevel, wordCloudDict, showPicture, outputFolder, dryRun, progress))
  else:
    i = 1
    for record in records:
      info("wordCloud: image %s" % (i), 1, progress)
      info("wordCloud: record = \n %s" %(record), 2, progress)
      genWordCloudDicts += genWordCloud(record[4], wordCloudTitle, removeStopwords, stopLevel, wordCloudDict, showPicture, outputFolder, dryRun, progress)
    i += 1

  return genWordCloudDicts
# wordCloud


def genWordCloud(text, wordCloudTitle, removeStopwords=True, level=0, wordCloudDict=wordCloudDict, showPicture=False, outputFolder=outputFolder, dryRun=False, progress=""):
  # wordCloudTitle = "KJZZ week=43 title=BBC World Service Day=Sat"
  info("Now generating: %s" %(wordCloudTitle), 2, progress)
  
  import numpy as np
  import pandas as pd
  import matplotlib
  # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
  if not showPicture: matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  from   matplotlib import style
  from   matplotlib.patches import Rectangle
  import seaborn
  from wordcloud import WordCloud
  # from wordcloud import STOPWORDS
  # print(STOPWORDS)

  genWordCloudDict = {
    "cleanWordsList": [], 
    "fileName": "", 
    "level": level, 
    "numWords": 0, 
    "outputFile": "", 
    "removeStopwords": removeStopwords, 
    "stopWords": [], 
    "text": text, 
    "top100tuples": [], 
    "wordCloudDict": wordCloudDict, 
    "wordCloudTitle": "", 
    "wordCloudTitle": wordCloudTitle, 
    "wordsList": [], 
  }

  # https://github.com/amueller/word_cloud/blob/main/examples/simple.py
  # we start by removing words from the wordCloudTitle of the show itself
  # for a typical week schedule, normally wordCloudTitle would be == "KJZZ week= title= Day="
  genWordCloudDict["stopWords"] = wordCloudTitle.replace("=", " ").split()
  genWordCloudDict["wordsList"] = text.split()
  genWordCloudDict["numWords"] = len(genWordCloudDict["wordsList"])
  genWordCloudDict["wordCloudTitle"] = "%s words=%s maxw=%s minf=%s maxf=%s scale=%s relscale=%s" % (
    genWordCloudDict["wordCloudTitle"], 
    genWordCloudDict["numWords"], 
    wordCloudDict["max_words"]["value"], 
    wordCloudDict["min_font_size"]["value"], 
    wordCloudDict["max_font_size"]["value"], 
    wordCloudDict["scale"]["value"], 
    wordCloudDict["relative_scaling"]["value"], 
  )
  genWordCloudDict["fileName"] = genWordCloudDict["wordCloudTitle"].replace(": ", "=").replace(":", "")
  genWordCloudDict["outputFileName"] = ""
  genWordCloudDict["outputFile"] = ""
  if dryRun: return genWordCloudDict

  if removeStopwords:
    stopwordsDict = loadStopWordsDict()
    
    for i in range(level + 1): genWordCloudDict["stopWords"] += stopwordsDict[i]
    genWordCloudDict["stopWords"] += wordCloudDict["inputStopWords"]["value"]
    # print(len(STOPWORDS))
    # STOPWORDS.update(genWordCloudDict["stopWords"]) # STOPWORDS is now listLevel 0 == stopwordsDict[0]
    # print(len(STOPWORDS))
    # print(len(stopWords))
    # print(stopWords)
    # WordCloud can remove stopWords by itself just fine, but we do it just have a count
    info("most 10 common words before: \n%s" % (Counter(genWordCloudDict["wordsList"]).most_common(10)), 2, progress)
    genWordCloudDict["cleanWordsList"] = [word for word in re.split("\W+",text) if word.lower() not in genWordCloudDict["stopWords"]]
    info("most 10 common words after: \n%s" % (Counter(genWordCloudDict["cleanWordsList"]).most_common(10)), 2, progress)
    genWordCloudDict["top100tuples"] = Counter(genWordCloudDict["cleanWordsList"]).most_common(100)
    info("%s words - %s stopWords (%s words removed) == %s total words" %(genWordCloudDict["numWords"], len(genWordCloudDict["stopWords"]), genWordCloudDict["numWords"] - len(genWordCloudDict["cleanWordsList"]), len(genWordCloudDict["cleanWordsList"])), 2, progress)
    info("stopWords = %s" %(str(genWordCloudDict["stopWords"])), 3, progress)
  else:
    info("%s words" %(genWordCloudDict["numWords"]), 1, progress)
  # image 1: Display the generated image:
  # font_path="fonts\\Quicksand-Regular.ttf"
  # class WordCloud: https://github.com/amueller/word_cloud/blob/fa7ac29c6c96c713f51585818e289e8f99c0f211/wordcloud/wordcloud.py#L154C25-L154C25
  wordcloud = WordCloud(
                        stopwords=genWordCloudDict["stopWords"], 
                        background_color=wordCloudDict["background_color"]["value"], 
                        max_words=wordCloudDict["max_words"]["value"], 
                        width=wordCloudDict["width"]["value"], 
                        height=wordCloudDict["height"]["value"], 
                        relative_scaling=wordCloudDict["relative_scaling"]["value"], 
                        normalize_plurals=wordCloudDict["normalize_plurals"]["value"], 
                        font_path=wordCloudDict["font_path"]["value"], 
                        min_word_length=wordCloudDict["min_word_length"]["value"], 
                        min_font_size=wordCloudDict["min_font_size"]["value"], 
                        max_font_size=wordCloudDict["max_font_size"]["value"], 
                        scale=wordCloudDict["scale"]["value"], 
                        collocation_threshold=wordCloudDict["collocation_threshold"]["value"], 
                        ).generate(text)
  # wordcloud.generate_from_frequencies(Counter(genWordCloudDict["cleanWordsList"]))
                        # stopwords=genWordCloudDict["stopWords"], 
                        # background_color=wordCloudDict["background_color"]["value"], 
                        # max_words=wordCloudDict["max_words"]["value"], 
                        # width=wordCloudDict["width"]["value"], 
                        # height=wordCloudDict["height"]["value"], 
                        # relative_scaling=wordCloudDict["relative_scaling"]["value"], 
                        # normalize_plurals=wordCloudDict["normalize_plurals"]["value"], 
                        # font_path=wordCloudDict["font_path"]["value"], 
                        # min_word_length=wordCloudDict["min_word_length"]["value"], 
                        # min_font_size=wordCloudDict["min_font_size"]["value"], 
                        # max_font_size=wordCloudDict["max_font_size"]["value"], 
                        # scale=wordCloudDict["scale"]["value"], 
                        # collocation_threshold=wordCloudDict["collocation_threshold"]["value"], 
                        # ).generate_from_frequencies(Counter(genWordCloudDict["cleanWordsList"]))
    
  # # trying to save image + add legend 1
  # plt.figure()
  # plt.imshow(wordcloud, interpolation='bilinear')
  # plt.axis("off")
  # # plt.switch_backend('Agg')
  # # plt.savefig(genWordCloudDict["wordCloudTitle"] + ".png")

  # # trying to save image + add legend 2
  # fig, ax = plt.subplots()
  # ax.imshow(wordcloud, interpolation='bilinear')
  # ax.axis("off")
  # # plt.switch_backend('Agg')
  # fig.savefig(genWordCloudDict["wordCloudTitle"] + ".png")
  # plt.title(genWordCloudDict["wordCloudTitle"])
  # # supported values are 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
  # # plt.legend(loc='best', fancybox=True, shadow=True)    # does not show in saved file
  # # fig.legend(fancybox=True, shadow=True)

  # trying to save image + add legend 3 - that one works
  # plt.subplots(figsize=(8, 4))  # 800 x 400
  plt.subplots(figsize=(20, 10))  # 2000 x 1000
  plt.title(genWordCloudDict["wordCloudTitle"])
  plt.axis("off")
  # plt.subplots_adjust(
    # top=0.931,
    # bottom=0.049,
    # left=0.017,
    # right=0.981,
    # hspace=0.2,
    # wspace=0.2
  # )
  # plt.tight_layout(pad=1)
  
  
  # self.layout_ = list(zip(frequencies, font_sizes, positions, orientations, colors))
  # print(wordcloud.layout_)
# [
    # (('museum', 1.0), 399, (594, 254), None, 'rgb(69, 55, 129)'),
    # (('women', 0.92), 383, (32, 286), None, 'rgb(72, 37, 118)'),
    # (('stories', 0.88), 375, (247, 345), None, 'rgb(41, 121, 142)'),
    # (('history', 0.76), 197, (812, 8), None, 'rgb(54, 92, 141)'),
    # (('music', 0.68), 187, (844, 1189), None, 'rgb(59, 82, 139)'),
    # (('tree', 0.68), 187, (37, 1611), None, 'rgb(58, 83, 139)'),
    # (('find', 0.56), 171, (364, 1672), None, 'rgb(239, 229, 28)'),
    # (('hand', 0.56), 171, (820, 781), None, 'rgb(189, 223, 38)'),
    # (('project', 0.56), 171, (4, 131), 2, 'rgb(54, 92, 141)'),
    # (('records', 0.56), 123, (498, 1539), None, 'rgb(152, 216, 62)'),
    # ...

  # self.words_ = dict(frequencies)
  # print(wordcloud.words_)
  # {
    # 'museum': 1.0,
    # 'women': 0.92,
    # 'stories': 0.88,
    # 'history': 0.76,
    # 'music': 0.68,
    # 'tree': 0.68,
    # 'find': 0.56,
    # 'hand': 0.56,
    # 'project': 0.56,
    # 'records': 0.56,
    # ...
  
  
  plt.imshow(wordcloud, interpolation='bilinear')

  # # image 2: lower max_font_size
  # wordcloud = WordCloud(max_font_size=40).generate(text)
  # plt.figure()
  # plt.imshow(wordcloud, interpolation="bilinear")
  # plt.axis("off")
  
  # The pil way (if you don't have matplotlib)
  # image = wordcloud.to_image()
  # image.show()
  
  # always save BEFORE show
  if genWordCloudDict["fileName"]: genWordCloudDict["outputFile"] = saveImage(outputFolder, genWordCloudDict["fileName"], plt, usePngquant, progress)
  if genWordCloudDict["outputFile"]:
    genWordCloudDict["outputFileName"] = os.path.basename(genWordCloudDict["outputFile"])
    genWordCloudDict["outputThumbnailFile"] = saveThumbnail(genWordCloudDict["outputFile"], outputFolder, "thumbnail-" + genWordCloudDict["outputFileName"], usePngquant)

  if showPicture: plt.show()
  plt.close()
  return genWordCloudDict
# genWordCloud


def loadStopWordsDict():
  from wordcloud import STOPWORDS
  # https://stackoverflow.com/questions/2831212/python-sets-vs-lists
  # z=set()
  # for word in stopwordsDict[4]:
    # if word not in STOPWORDS: z.add(word)   --> now you have a cleaned set of words not already in STOPWORDS
  
  # each stopwords list is actually a set. it's faster to check for word in set then in list, or so they say
  stopwordsDict = {
    0: STOPWORDS,
  }
  
  # TODO: what do we do with stopWords.Wordlist-Adjectives-All.txt? it also contains words, not just adjectives
  stopWordsFileNames = ['dummy', 'stopWords.1.txt', 'stopWords.kjzz.txt', 'stopWords.ranks.nl.uniq.txt']
  for index, stopWordsFileName in enumerate(stopWordsFileNames):
    info("index=%s, stopWordsFileName=%s" %(index, stopWordsFileName), 2)
    stopWordsFile = os.path.join(dataFolder, stopWordsFileName)
    if os.path.isfile(stopWordsFile):
      stopwordsDict[index] = set()
      with open(stopWordsFile, 'r') as fd:
        for line in fd:
          word = line.strip()
          stopwordsDict[index].add(word)

  return stopwordsDict
# loadStopWordsDict


def loadDictHeatMap(dictHeatMap, withSynonyms=withSynonyms):
  synonymsFile = os.path.join(thesaurusFolder, 'Thesaurus-Synonyms-Common.txt')
  # only the synonyms of sourcing and uncertainty seem to make sense, and look the most closely related
  heatFactorSynonymsFor = set({"sourcing", "uncertainty"})
  
  # load the sets of heat words
  for heatFactor in dictHeatMap.keys():
    heatFactorFile = os.path.join(dataFolder, 'heatMap.'+heatFactor+'.csv')
    heatFactorWSynonymsFile = os.path.join(dataFolder, 'heatMap.'+heatFactor+'+synonyms.csv')
    synonymsList = set()
    
    # synonyms wanted and available:
    if heatFactor in heatFactorSynonymsFor and withSynonyms:
      if not force and os.path.isfile(heatFactorWSynonymsFile) and os.path.getsize(heatFactorWSynonymsFile) > os.path.getsize(heatFactorFile):
        info("%s: open file %s" %( heatFactor, heatFactorWSynonymsFile), 3)
        with open(heatFactorWSynonymsFile, 'r') as fd:
          # BUGFIX: split() also splits compound words like "according to" so we resort to .strip().split('\n')
          dictHeatMap[heatFactor]["words"].update(fd.read().strip().split('\n'))
      else:
        # load the whole synonyms file only once
        if not synonymsList:
          info("%s: open file %s" %( heatFactor, synonymsFile), 3)
          with open(synonymsFile, 'r') as fd: synonymsList.update(fd.read().strip().split('\n'))
        info("%s: open file %s" %( heatFactor, heatFactorFile), 3)
        with open(heatFactorFile, 'r') as fd: words = fd.read().strip().split('\n')

        for word in words:
          dictHeatMap[heatFactor]["words"].add(word)
          for synonym in synonymsList:
            # match will only match first word == first line found
            if re.match(re.escape(word+"|"), synonym):
              # split line found and update the set()
              synonyms = re.split(r"[|,]", synonym.strip())
              info("%s: synonyms of %s = %s" %( heatFactor, word, synonyms), 3)
              dictHeatMap[heatFactor]["words"].update(synonyms)
              break
          
        # and finally we save it to not redo it again:
        if not dryRun:
          info("%s: save file %s" %( heatFactor, heatFactorWSynonymsFile), 3)
          with open(heatFactorWSynonymsFile, 'w') as fd:
            fd.write('\n'.join(dictHeatMap[heatFactor]["words"]))
    
    # no synonyms wanted or unavailable:
    else:
      info("%s: open file %s" %( heatFactor, heatFactorFile), 3)
      with open(heatFactorFile, 'r') as fd: words = fd.read().strip().split('\n')
      dictHeatMap[heatFactor]["words"].update(words)

    info("%s: words = %s" %( heatFactor, len(dictHeatMap[heatFactor]["words"]) ), 3)
    info("%s: words: %s" %( heatFactor, dictHeatMap[heatFactor]["words"]), 4)

  return dictHeatMap
# loadDictHeatMap


def genMisInformation(records, mergeRecords, graphTitle, graphs, showPicture=False, dryRun=False):
  # gettext = "week=43+title=Classic Jazz with Chazz Rayburn+Day=Mon"
  # gettextDict = {'week': '43', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
  # records = [('2023-10-14 01:00.000', '2023-10-14 01:30.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...')..]
  if len(records) == 0: return []
  mergedText = ''
  dictHeatMap = loadDictHeatMap(dictHeatMapBlank, withSynonyms)
              # dictHeatMapBlank = { 
                # "explanatory":{"words":set(),"heatCount":0,"heat":0.0}, 
                # ..
  
  # useful for whole segments:
  if mergeRecords:
    for record in records:
      # startDict   = TimeDict(record[0])
      # stopDict    = TimeDict(record[1])
      # chunkName   = record[2]
      misInfoText = record[3]
      text        = record[4]
      mergedText += text
      
      # shortcut: pre-load retrieved misInfo values into "heat" when they exist. 
      # dictHeatMapBlank.keys() are assumed to be in same order as the misInfo list items
      # BUG: We also assume all chunks of a processed segment have been processed and no item in misInfo is=None
      if misInfoText is not None and not force:
        for index, heatFactor in enumerate(dictHeatMap.keys()):
          if dictHeatMap[heatFactor]["heat"] is None:
            dictHeatMap[heatFactor]["heat"]  = json.loads(misInfoText)[index]
          else:
            dictHeatMap[heatFactor]["heat"] += json.loads(misInfoText)[index]
    
    # and finally, we average this heat. 
    # TODO: Maybe modal is more useful, we don't know yet
    for heatFactor in enumerate(dictHeatMap.keys()):
      dictHeatMap[heatFactor]["heat"] = dictHeatMap[heatFactor]["heat"] / len(records)
      
    genMisinfoDicts = genMisinfoBarGraph(mergedText, graphTitle, dictHeatMap, wordCloudDict, graphs, showPicture, dryRun)
    info(genMisinfoDicts, 4, progress)
    # {'heatMaps': [ [0.7, 0.4, 0.4, 2.9] ], 'Xlabels': .. }
    
  # useful for chunks or db_update:
  else:
    # let's pass the records directly, this way genMisinfoHeatMap has an opportunity to get chunk names as well
    # textArray = []
    # Ylabels = []
    dictHeatMaps = []
    for record in records:
      # startDict   = TimeDict(record[0])
      # stopDict    = TimeDict(record[1])
      # chunkName   = record[2]
      misInfoText = record[3]
      # text        = record[4]

      # shortcut: pre-load retrieved misInfoText values into "heat" when they exist. 
      # dictHeatMapBlank.keys() are assumed to be in same order as the misInfo list items
      # BUG: We also assume all chunks of a processed segment have been processed and no item in misInfo is=None
      if misInfoText is not None and not force:
        for index, heatFactor in enumerate(dictHeatMap.keys()):
          dictHeatMap[heatFactor]["heat"] = json.loads(misInfoText)[index]
          
      # we need a deepcopy of dictHeatMap or they will all be pointing to the same one
      dictHeatMaps.append(copy.deepcopy(dictHeatMap))

    # genMisinfoDicts = genMisinfoHeatMap(textArray, Ylabels, graphTitle, dictHeatMaps, wordCloudDict, showPicture, dryRun)
    genMisinfoDicts = genMisinfoHeatMap(records, graphTitle, dictHeatMaps, wordCloudDict, showPicture, dryRun)
    info(genMisinfoDicts, 4, progress)
    # ddebug(genMisinfoDicts)
    # {
    # 'heatMaps': [
        # [0.7, 0.4, 0.4, 2.9],
        # ..
        # [0.4, 0.4, 0.3, 2.3]
      # ],
    # 'Xlabels': ['explanatory', 'retractors', 'sourcing', 'uncertainty'],
    # 'Ylabels': [
        # '03:00',
        # ..
        # '08:30'
      # ]
    # }
    
    
  # genMisinfoDicts = {"heatMaps":heatMaps, "Xlabels":Xlabels, "Ylabels":Ylabels}
  return genMisinfoDicts
#


def genMisinfoBarGraph(text, graphTitle, dictHeatMap, wordCloudDict=wordCloudDict, graphs=defaultGraphs, showPicture=False, dryRun=False, progress=""):
  info("%s" %(graphTitle), 2)
  textWordsLen = len(text.strip().split())
  if len(graphs) == 0: graphs=defaultGraphs

  # load the sets of heat words
  for heatFactor in dictHeatMap.keys():
    if dictHeatMap[heatFactor]["heat"] is None or force:
      # count occurences in the text
      for word in dictHeatMap[heatFactor]["words"]:
        # print("  "+word)
        dictHeatMap[heatFactor]["heatCount"] += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text))
        
      dictHeatMap[heatFactor]["heat"] = ( 100 * dictHeatMap[heatFactor]["heatCount"] / textWordsLen )
      info("%s heatCount %s" %( heatFactor, dictHeatMap[heatFactor]["heatCount"] ), 2, progress)
      info("%s heat      %s" %( heatFactor, dictHeatMap[heatFactor]["heat"] ), 2, progress)
    
  
  Xlabels = dictHeatMap.keys()
  Ylabels = []
  for dictFactor in dictHeatMap.values():
    Ylabels.append(dictFactor["heat"])
  
  partialFileName = graphTitle.replace(": ", "=").replace(":", "")
  if not noPics:
    if "bar"  in graphs: graph_bar(Xlabels, Ylabels, graphTitle,  "misInformation bar "+partialFileName)
    if "pie"  in graphs: graph_pie(Xlabels, Ylabels, graphTitle,  "misInformation pie "+partialFileName)
    if "line" in graphs:                     graph_line(Xlabels, Ylabels, graphTitle, "misInformation line "+partialFileName)

  return {"heatMaps":[Ylabels], "Xlabels":Xlabels, "Ylabels":Ylabels}
# genMisinfoBarGraph


# python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --noMerge   --show
# def genMisinfoHeatMap(textArray, Ylabels, graphTitle, dictHeatMaps, wordCloudDict=wordCloudDict, showPicture=False, dryRun=False, progress=""):
def genMisinfoHeatMap(records, graphTitle, dictHeatMaps, wordCloudDict=wordCloudDict, showPicture=False, dryRun=False, progress=""):
  # records = [('2023-10-14 01:00:00.000', '2023-10-14 01:30:00.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...'),..]
  
  info("%s showPicture=%s dryRun=%s" %(graphTitle, showPicture, dryRun), 1, progress)
  heatMaps = []
  Xlabels = list(dictHeatMaps[0].keys())  # just grab the heatFactor labels from the first one
  Ylabels = []

  with Progress() as progress:
    task = progress.add_task("BSoMeter running", total=len(records))
    for index, record in enumerate(records):
      startDict   = TimeDict(record[0])
      # stopDict    = TimeDict(record[1])
      chunkName   = record[2]
      misInfoText = record[3]
      Ylabels.append(startDict.HHMM)
      text = record[4]
      
      if misInfoText is None or force:
        textWordsLen = len(text.strip().split())
        if len(text) < minChunkSize:
          # warning("%s[%s]: chunkSize %s < %s minChunkSize at %s:" %(graphTitle, index, len(text), minChunkSize, Ylabels[index]), 0, progress)
          warning('%s[%s] chunkSize %s < %s minChunkSize "%s"' %(graphTitle, index, len(text), minChunkSize, chunkName), 0, progress)
          if verbose > 2: warning(dictHeatMaps[index], 0, progress)
          if verbose > 3: warning(text, 0, progress)
        
        # build the lists of heat words
        for heatFactor in Xlabels:
          # count occurences in the text
          for word in dictHeatMaps[index][heatFactor]["words"]:
            # print("  "+word)
            dictHeatMaps[index][heatFactor]["heatCount"] += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text))
            
          dictHeatMaps[index][heatFactor]["heat"] = round( 100 * dictHeatMaps[index][heatFactor]["heatCount"] / textWordsLen , 1 )
          info('%s[%s] processd: %11s heatCount %3s "%s"' %( graphTitle, index, heatFactor, dictHeatMaps[index][heatFactor]["heatCount"], chunkName), 3, progress)
          info('%s[%s] processd: %11s heat      %3s "%s"' %( graphTitle, index, heatFactor, dictHeatMaps[index][heatFactor]["heat"], chunkName), 3, progress)
      else:
        misInfo = json.loads(misInfoText)
        for num, heatFactor in enumerate(Xlabels):
          dictHeatMaps[index][heatFactor]["heat"] = misInfo[num]
          info('%s[%s] database: %11s heat      %3s "%s"' %( graphTitle, index, heatFactor, dictHeatMaps[index][heatFactor]["heat"], chunkName), 3, progress)
          
      
      Y = []
      Ytotal = 0.0
      for dictFactor in dictHeatMaps[index].values():
        Y.append(dictFactor["heat"])
        Ytotal += dictFactor["heat"]
      if Ytotal == 0.0:
        # warning("%s[%s]: heatFactors are null at %s" %(graphTitle, index, Ylabels[index]), 0, progress)
        warning('%s[%s] heatFactors are null for "%s"' %(graphTitle, index, chunkName), 0, progress)
        if verbose > 2: warning(dictHeatMaps[index], 0, progress)
        if verbose > 3: warning(text, 0, progress)
        
      heatMaps.append(Y)
      progress.advance(task)
      
  fileName = "misInformation heatMap " + graphTitle.replace(": ", "=").replace(":", "")
               # graph_heatMap(arrays,   Xlabels, Ylabels, graphTitle="", fileName="", showPicture=False, progress=""):
  if not noPics: graph_heatMap(heatMaps, Xlabels, Ylabels, graphTitle, fileName, showPicture)
  
  return {"heatMaps":heatMaps, "Xlabels":Xlabels, "Ylabels":Ylabels}
# genMisinfoHeatMap



def readInputFolder(inputFolder):
  if os.path.isdir(inputFolder):
    info(("listing folder %s ...") % (inputFolder), 1)
    # inputFiles = sorted([os.fsdecode(file) for file in os.listdir(inputFolder) if os.fsdecode(file).endswith(".text")])
    # inputFiles = sorted([os.path.join(inputFolder, file) for file in os.listdir(inputFolder) if os.fsdecode(file).endswith(".text")] , key=os.path.getctime)
    inputFiles = [str(child.resolve()) for child in Path.iterdir(Path(inputFolder)) if os.fsdecode(child).endswith(".text")]
    
    for inputFile in inputFiles:
      if (os.path.getsize(inputFile) == 0):
        if verbose: print(("    %s is empty") % (inputFile))
        inputFiles.remove(inputFile)
      
    return inputFiles
  else:
    error("%s not found" % (inputFolder))
  #
# readInputFolder


def readInputFile(inputTextFile):
  if os.path.isfile(inputTextFile):
    if (os.path.getsize(inputTextFile) > 0):
      info("inputTextFile %s passed" % (inputTextFile), 1)
      return [inputTextFile]
    else:
      info("%s is empty" % (inputTextFile), 1)
  else:
    error("%s not found" % (inputTextFile))
  #
# readInputFile



def graph_line(X, Y, title="", fileName="", progress=""):
  import numpy as np
  import pandas as pd
  import matplotlib
  # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
  if not showPicture: matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  from   matplotlib import style
  from   matplotlib.patches import Rectangle
  import seaborn

  # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot_date.html
  plt.plot_date(X,Y,linestyle='solid')
  plt.xticks(rotation=45)
  plt.ylabel('count')
  plt.xlabel('date')

  # always save BEFORE show
  if fileName: outputFile = saveImage(outputFolder, fileName, plt, usePngquant, progress)

  if showPicture: plt.show()
  plt.close()
  return outputFile
# graph_line


# python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --graph bar --show
def graph_bar(X, Y, title="", fileName="", progress=""):
  import numpy as np
  import pandas as pd
  import matplotlib
  # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
  if not showPicture: matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  from   matplotlib import style
  from   matplotlib.patches import Rectangle
  import seaborn

  # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
  plt.bar(X,Y)
  plt.xticks(rotation=45)
  plt.ylabel('count')
  plt.xlabel('date')

  # always save BEFORE show
  if fileName: outputFile = saveImage(outputFolder, fileName, plt, usePngquant, progress)

  if showPicture: plt.show()
  plt.close()
  return outputFile
# graph_bar


# python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --graph pie --show
def graph_pie(X, Y, title="", fileName="", progress=""):
  import numpy as np
  import pandas as pd
  import matplotlib
  # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
  if not showPicture: matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  from   matplotlib import style
  from   matplotlib.patches import Rectangle
  import seaborn

  # https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_features.html#sphx-glr-gallery-pie-and-polar-charts-pie-features-py
  # fig, ax = plt.subplots(figsize=(20, 10))  # 2000 x 1000
  fig, ax = plt.subplots()
  ax.pie(Y, labels=X)
  ax.set_title(title)
  ax.axis("off")

  # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
  # savefig(fname, *, transparent=None, dpi='figure', format=None,
        # metadata=None, bbox_inches=None, pad_inches=0.1,
        # facecolor='auto', edgecolor='auto', backend=None,
        # **kwargs
       # )
       
  # always save BEFORE show
  if fileName: outputFile = saveImage(outputFolder, fileName, plt, usePngquant, progress)

  if showPicture: plt.show()
  plt.close()
  return outputFile
# graph_pie


def graph_heatMapTestHighlight(progress=""):
  import numpy as np
  import pandas as pd
  import matplotlib
  # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
  if not showPicture: matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  from   matplotlib import style
  from   matplotlib.patches import Rectangle
  import seaborn

  labels = list('abcdef')
  N = len(labels)
  ax = seaborn.heatmap(np.random.uniform(0, 1, (N, N)), cmap='summer', annot=True, linewidths=.5,
                   xticklabels=labels, yticklabels=labels)
  wanted_label = 'c'
  wanted_index = labels.index(wanted_label)
  x, y, w, h = 0, wanted_index, N, 1
  for _ in range(2):
      ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor='crimson', lw=4, clip_on=False))
      x, y = y, x # exchange the roles of x and y
      w, h = h, w # exchange the roles of w and h
  ax.tick_params(length=0)

  # always save BEFORE show
  if fileName: outputFile = saveImage(outputFolder, fileName, plt, usePngquant, progress)

  if showPicture: plt.show()
  plt.close()
  return outputFile
# graph_heatMapTestHighlight


# python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --noMerge   --show
def graph_heatMap(arrays, Xlabels, Ylabels, graphTitle="", fileName="", showPicture=False, progress=""):
  import numpy as np
  import pandas as pd
  import matplotlib
  # https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
  if not showPicture: matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  import matplotlib.dates as mdates
  from   matplotlib import style
  from   matplotlib.patches import Rectangle
  import seaborn

  # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
  # https://seaborn.pydata.org/tutorial/color_palettes.html
  # https://stackoverflow.com/questions/62533046/how-to-add-color-border-or-similar-highlight-to-specifc-element-of-heatmap-in-py
  info("title    = "+graphTitle, 2)
  info("fileName = "+fileName, 2)
  # graphTitle = "Harvest of local farmers (in tons/year)"
  # Ylabels = ["cucumber", "tomato", "lettuce", "asparagus",
                # "potato", "wheat", "barley"]
  # Xlabels = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
             # "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]
  # indices = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
                      # [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
                      # [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
                      # [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
                      # [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
                      # [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
                      # [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])
  indices = np.array(arrays)
  fig, ax = plt.subplots()

  # default heatMap: 
  # im = ax.imshow(indices)
  

  # seaborn heatMap: 
  # cmap='summer'
  # cmap='coolwarm'
  # cmap='Spectral'
  # cmap='Spectral'
  ax = seaborn.heatmap(indices, cmap='YlOrBr', annot=True, linewidths=.5, xticklabels=Xlabels, yticklabels=Ylabels)

  # Loop over data dimensions and create text annotations at each top-left corner
  # for x in range(len(Ylabels)):
    # for y in range(len(Xlabels)):
      # text = ax.text(y, x, indices[x, y], ha="center", va="center", color="y")

  # get Xindex of sourcing as the start column. we want to highlight 2 columns only.
  # "sourcing" is the 3rd column
  Xindex = Xlabels.index("sourcing")
  Xwidth = 2
  # Yindex = Ylabels.index("04:30")
  Yheight = 1
  # x, y, w, h = Xindex, Yindex, Xwidth, Yheight
  # this is very specific: we KNOW Xindex = 2 is sourcing and Xindex +1 = uncertainty
  for x in range(Xindex, len(Xlabels) - 1):
    for y in range(len(Ylabels)):
      # we only divide by uncertainty because it's never == 0 while sourcing can be == 0
      sourcing    = indices[y][x]
      uncertainty = indices[y][x+1]
      
      # we want RED   when sourcing is low and uncertainty is high       : missing sources and complete BS
      BSoMeter = round((uncertainty - sourcing) / uncertainty, 2)
      if BSoMeter >= BSoMeterTrigger:
        edgecolor = 'orange'
        if BSoMeter >  BSoMeterLevel2: edgecolor = 'crimson'
        ax.add_patch(Rectangle((x, y), Xwidth, Yheight, fill=False, edgecolor=edgecolor, lw=4, clip_on=False))

      # we want RED   when sourcing is low and uncertainty is low        : missing sources
      # if ((uncertainty - sourcing)/uncertainty < 0.8 and sourcing <= 0.2):
        # ax.add_patch(Rectangle((x, y), Xwidth, Yheight, fill=False, edgecolor='crimson', lw=4, clip_on=False))

      # we want RED   when sourcing is high and uncertainty is high : makes no sense
      # if (uncertainty - sourcing)/uncertainty < 0.6:
        # ax.add_patch(Rectangle((x, y), Xwidth, Yheight, fill=False, edgecolor='crimson', lw=4, clip_on=False))

  # hide ticks`:
  # ax.tick_params(length=0)
  
  # Rotate the tick labels and set their alignment.
  # We don't need that with seaborn as the cells are much wider
  # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
           # rotation_mode="anchor")
  
  # graphTitle and layout must be set AT THE END or they will be cut
  ax.set_title("misInformation heatMap\n"+graphTitle)
  fig.tight_layout()

  # always save BEFORE show
  if fileName: outputFile = saveImage(outputFolder, fileName, plt, usePngquant, progress)

  if showPicture: plt.show()
  plt.close()
  return outputFile
# graph_heatMap


def saveImage(outputFolder, fileName, plt, usePngquant=usePngquant, progress=""):
  if useJpeg:
    outputFileName = fileName + ".jpg"
    outputFile = os.path.join(outputFolder, outputFileName)
    plt.savefig(outputFile, pil_kwargs={
                            'quality': jpegQuality,
                            'subsampling': 10
                            })
  else:
    outputFileName = fileName + ".png"
    outputFile = os.path.join(outputFolder, outputFileName)
    plt.savefig(outputFile, bbox_inches='tight')
    if usePngquant:
      import pngquant
      pngquant.config(min_quality=1, max_quality=20, speed=1, ndeep=2)
      pngquant.quant_image(image=outputFile)
  info('image saved: "%s" [%.0fk]' %(outputFile, os.path.getsize(outputFile)/1024), 1, progress)
  return outputFile
# saveImage


def saveThumbnail(inputFile, outputFolder, thumbnailFileName, usePngquant=usePngquant, progress=""):
  import PIL

  # I would love this to work instead of reloading the file we just produced:
  # PILoutputFile = PIL.Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
  PILoutputFile = PIL.Image.open(inputFile)
  PILoutputFile.thumbnail((256, 256), PIL.Image.Resampling.LANCZOS)   # looks okay
  # PILoutputFile = thumbnail.resize((256,256), PIL.Image.LANCZOS)    # does not look good
  
  thumbnailFile = os.path.join(outputFolder, thumbnailFileName)
  if useJpeg:
    PILoutputFile.save(thumbnailFile , "JPEG", quality=jpegQuality, optimize=True)
  else:
    PILoutputFile.save(thumbnailFile)
    if usePngquant:
      import pngquant
      # for clean, electronically generated graphs, pngquant will always give better results than jpeg 50%
      pngquant.config(min_quality=1, max_quality=20, speed=1, ndeep=2)
      pngquant.quant_image(image=thumbnailFile)

  info('thumbnail saved: "%s" [%.0fk]' %(thumbnailFile, os.path.getsize(thumbnailFile)/1024), 2, progress)
  return thumbnailFile
#



# jsonSchedule looks like this, with every hour in a day, except where we have half-hour programs
# {
    # '00:00': {
        # 'Mon': 'BBC World Service',
        # 'Tue': 'Classic Jazz with Chazz Rayburn',
        # 'Wed': 'Classic Jazz with Bryan Houston',
        # 'Thu': 'Classic Jazz with Bryan Houston',
        # 'Fri': 'Classic Jazz with Michele Robins',
        # 'Sat': 'Classic Jazz with Michele Robins',
        # 'Sun': 'BBC World Service'
    # },
    # '01:00': {
def getNextKey(HHMMList, key):
  if key+1 < len(HHMMList):
    # print("len=%s HHMMList[%s] = %s" %(len(HHMMList), key, HHMMList[key]))
    return HHMMList[key+1]
  else:
    return None

def getPrevKey(HHMMList, key):
  if key > 0:
    # print("len=%s HHMMList[%s] = %s" %(len(HHMMList), key, HHMMList[key]))
    return HHMMList[key-1]
  else:
    return None


def rebuildThumbnails(inputFolder, outputFolder, dryRun=False, progress=""):
  pngPath = '%s/KJZZ*.png' %(inputFolder)
  pngList = glob.glob(pngPath, recursive=False)
  # print(pngList)

  with Progress() as progress:
    task = progress.add_task("Thumbnail gen", total=len(pngList))
    for png in pngList:
      outputThumbnailFile = saveThumbnail(png, outputFolder, "thumbnail-" + os.path.basename(png), usePngquant)
      progress.advance(task)
  
# rebuildThumbnails


def genHtmlHead(pageTitle):
  dictTemplate = dict(pageTitle=pageTitle, rand1=random.randint(0,99))
  template = string.Template(('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="ie=edge" />
  
  <title data-l10n-id="${pageTitle}"></title>

  <link rel="stylesheet" href="../fonts/css/fontawesome.min.css">
  <link rel="stylesheet" href="../fonts/css/regular.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/openplayerjs@1.12.1/dist/openplayer.min.css">
  <link rel="stylesheet" href="../style.css?${rand1}">

</head>
'''))
  return template.substitute(dictTemplate)

# genHtmlModal


def genHtmlModal():
  return '''
<div id="modal-root">
  <div id="modal-bg" onclick="onClickModalBackdrop(this)"></div>
  <div id="modal" class="zoom_outer" onclick="onClickModalBackdrop(this)">
    <i id="modal-close-btn" onclick="onClickModalCloseBtn(this)" class="fa-regular fa-window-close"></i>
    <div id="zoom">
      <img id="modal-img" decoding="async" loading="lazy" onclick="onClickImgPrevent(event);" />
    </div>
  </div>
</div>
'''
# genHtmlModal

def genHtmlThead(weekNumber, byChunk):
  addByChunk = '-byChunk'
  addNotByChunk = ''
  switchTo = 'byChunk'
  if byChunk:
    addByChunk = ''
    addNotByChunk = '-byChunk'
    switchTo = 'bySchedule'

  dictTemplate = dict(weekNumber=weekNumber, prevWeekNumber=(weekNumber-1), nextWeekNumber=(weekNumber+1), addNotByChunk=addNotByChunk, addByChunk=addByChunk, switchTo=switchTo)
  template = string.Template(('''
<thead>
  <tr class="title">
    <td><span><a class="prevWeek" href="../${prevWeekNumber}/index${addNotByChunk}.html">&larr; week ${prevWeekNumber}</a></span></td>
    <td colspan="6"><span>KJZZ week ${weekNumber}<a href="index${addByChunk}.html">&nbsp;&nbsp;&nbsp;${switchTo}</a></span></td>
    <td><span><a class="nextWeek" href="../${nextWeekNumber}/index${addNotByChunk}.html">week ${nextWeekNumber}&rarr;</a></span></td>
  </tr>
  <tr>
    <th class="startTime">Time</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th>
  </tr>
</thead>
'''))
  return template.substitute(dictTemplate)

# genHtmlThead


def genHtmlChunk(rowspan, classChunkExist, title, plays, texts, segmentImg=""):
  dictTemplate = dict(rowspan=rowspan, classChunkExist=classChunkExist, title=title, plays=plays, texts=texts, segmentImg=segmentImg)
  template = string.Template(('''
<td rowspan="${rowspan}" ${classChunkExist}>
  <div>
    <span>${title}</span>
    <span class="block">${plays}</span>
    <span class="block">${texts}</span>
  </div>
  ${segmentImg}
</td>
'''))
  return template.substitute(dictTemplate)

# <td rowspan="5" class="chunkExist">
  # <div>
    # <span>BBC World Service</span>
    # <span>
      # <i class="fa-regular fa-circle-play tooltip" onclick="play('KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.mp3');"><span class="tooltiptext tooltipBottomLeft"><div>23:00 - 23:30<br>KJZZ_2023-10-08_Sun_2300-2330_BBC World Service</div></span></i>
      # <i class="fa-regular fa-circle-play tooltip" onclick="play('KJZZ_2023-10-08_Sun_2330-0000_BBC World Service.mp3');"><span class="tooltiptext tooltipBottomLeft"><div>23:30 - 00:00<br>KJZZ_2023-10-08_Sun_2330-0000_BBC World Service</div></span></i>
    # </span>
    # <span>
      # <a href="KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.text"><i class="fa-regular fa-file-lines" ></i></a>
      # <a href="KJZZ_2023-10-08_Sun_2330-0000_BBC World Service.text"><i class="fa-regular fa-file-lines" ></i></a>
    # </span>
  # </div>
  # <div onclick="showModal('KJZZ week=40 title=BBC World Service Day=Sun words=8628 maxw=1000 minf=4 maxf=400 scale=1.0 relscale=auto.png');">
    # <img src="thumbnail-KJZZ week=40 title=BBC World Service Day=Sun words=8628 maxw=1000 minf=4 maxf=400 scale=1.0 relscale=auto.png" alt="KJZZ week=40 title=BBC World Service Day=Sun words=8628 maxw=1000 minf=4 maxf=400 scale=1.0 relscale=auto.png" class="chunkExist" decoding="async" onerror="this.src='../missingCloud.png'" loading="lazy" />
  # </div>
# </td>

# genHtmlChunk


def genHtmlFooter():
  dictTemplate = dict(rand1=random.randint(0,99), rand2=random.randint(0,99))
  template = string.Template(('''
<script src="https://cdn.jsdelivr.net/npm/openplayerjs@latest/dist/openplayer.min.js"></script>
<script src="../OpenPlayerJS.js?${rand1}"></script>
<script src="../ui.js?${rand2}"></script>
'''))
  return template.substitute(dictTemplate)

# genHtmlFooter


def genSegmentImg(imgFileName, classChunkExist):
  thumbnailFileName = "thumbnail-%s" %(imgFileName)

  dictTemplate = dict(imgFileName=imgFileName, thumbnailFileName=thumbnailFileName, classChunkExist=classChunkExist)
  template = string.Template(('''
    <div onclick="showModal('${imgFileName}');">
      <img width="256" src="${thumbnailFileName}" alt="${imgFileName}" ${classChunkExist} decoding="async" onerror="this.src='../missingCloud.png';" loading="lazy" />
    </div>
'''))
  return template.substitute(dictTemplate)

# <div onclick="showModal('KJZZ week=40 title=BBC World Service Day=Sun words=8628 maxw=1000 minf=4 maxf=400 scale=1.0 relscale=auto.png');">
  # <img src="thumbnail-KJZZ week=40 title=BBC World Service Day=Sun words=8628 maxw=1000 minf=4 maxf=400 scale=1.0 relscale=auto.png" alt="KJZZ week=40 title=BBC World Service Day=Sun words=8628 maxw=1000 minf=4 maxf=400 scale=1.0 relscale=auto.png" class="chunkExist" decoding="async" onerror="this.src='../missingCloud.png'" loading="lazy" />
# </div>
# genSegmentImg


def genPlayButton(startTime, stopTime, fileStem, misInfoText, misInfoLabels, classTooltipPosition, progress=""):
  # misInfoText = '[0.7, 0.4, 0.4, 2.9]' or None
  colorClass = ''
  BSoMeterTable = ''
  misInfoHtmlTemplate = ''
  BSoMeterTriggerClass = ''
  if misInfoText:
    misInfo = json.loads(misInfoText)
    info(misInfoText, 3, progress)
    misInfoHtmlTemplate = '<ul class="alignLeft">'
    for index, label in enumerate(misInfoLabels):
      misInfoHtmlTemplate += '<li>%s: %s</li>' %(label, misInfo[index])
      
    BSoMeter = 0.0
    if misInfo[3] > 0.0:
      BSoMeter = round((misInfo[3] - misInfo[2]) / misInfo[3], 2)
    misInfoHtmlTemplate += '<li class="BSoMeter ${BSoMeterTriggerClass}">%s: %s</li>' %('BSoMeter', BSoMeter)
    misInfoHtmlTemplate += '</ul>'
    if BSoMeter >= BSoMeterTrigger:
      info("%s BSoMeter: %s >= %s" %(fileStem, BSoMeter, BSoMeterTrigger), 3, progress)
      BSoMeterTriggerClass = 'BSoMeterTrigger'
      colorClass = 'roundRed'
      if BSoMeter >  BSoMeterLevel2: colorClass = 'roundCrimson'
  
  misInfoHtml = string.Template(misInfoHtmlTemplate).substitute(dict(BSoMeterTriggerClass=BSoMeterTriggerClass))
  
  dictTooltipTemplate = dict(fileStem=fileStem, classTooltipPosition=classTooltipPosition, startTime=startTime, stopTime=stopTime, misInfoHtml=misInfoHtml)
  tooltipTemplate = string.Template(('''
        <span class="tooltiptext ${classTooltipPosition}">
          <div>
            <span>${startTime} - ${stopTime}</span>
            <span>${fileStem}</span>
            <span>${misInfoHtml}</span>
          </div>
        </span>
'''))
  tooltip = tooltipTemplate.substitute(dictTooltipTemplate)


  dictTemplate = dict(fileStem=fileStem, colorClass=colorClass, tooltip=tooltip)
  template = string.Template(('''
      <i class="fa-regular fa-circle-play tooltip ${colorClass}" onclick="play('${fileStem}.mp3');">
${tooltip}
      </i>
'''))
  return template.substitute(dictTemplate)

# genPlayButton


def genTextButton(fileStem, progress=""):
  dictTemplate = dict(fileStem=fileStem)
  template = string.Template(('''
      <a href="${fileStem}.text">
        <i class="fa-regular fa-file-lines tooltip" ></i>
      </a>
'''))
  return template.substitute(dictTemplate)

# genTextButton


def genHtml(jsonScheduleFile, outputFolder, weekNumber, byChunk=False):
  
  # old school:
  # pngList = []
  # for file in os.listdir(outputFolder):
    # if file.endswith('.png'):
      # pngList.append(file)

  # better school:
  pngPath = '%s/KJZZ week=%s*.png' %(os.path.join(outputFolder, str(weekNumber)), weekNumber)
  pngList = glob.glob(pngPath, recursive=False)

  # regexp = re.compile("^KJZZ week=%s.*title=%s.*Day=%s" %(weekNumber, "The Moth", "Sat"))
  # print(list(filter(regexp.match, pngList)))
  # exit()

  # load json
  if os.path.isfile(jsonScheduleFile):
    with open(jsonScheduleFile, 'r') as fd:
      jsonSchedule = json.load(fd)
      
    # # alternatively, the old way:
    # f = open(jsonScheduleFile)
    # jsonSchedule = json.load(f)
    # f.close()

  # how do my table compare to https://kjzz.org/kjzz-print-schedule ? let me know in the comments!
  
  html  = genHtmlHead("%s week %s" %("KJZZ", weekNumber))
  html += '<body>\n'
  html += genHtmlModal()
  
  # https://github.com/openplayerjs/openplayerjs/blob/master/docs/api.md
  # https://github.com/openplayerjs/openplayerjs/blob/master/docs/usage.md
  
  html += '<table>\n'
  html += genHtmlThead(weekNumber, byChunk)
  html += '<tbody>\n'
  
  rowspanDict       = {}
  HHMMList          = list(jsonSchedule.keys())
  reversedHHMMList  = list(reversed(HHMMList))
  DayList           = list(jsonSchedule[reversedHHMMList[0]].keys())
  rowspan           = {}
  if byChunk:
    outputFileName = "index-byChunk.html"
  else:
    outputFileName = "index.html"

  info("DayList: %s" %(DayList), 2)
  for Day in DayList: rowspan[Day] = 1
  
  with Progress() as progress:
    task = progress.add_task("Building %s ..." %(outputFileName), total=len(reversedHHMMList)*len(DayList))
    
    # We reverse because that's the only way to increase the rowspan of the first occurance of the same title.
    # Also we read each startTime and may end up regenerating the same wordClouds, 
    #   so we need to check if it was not generated at some point. This is inefficient.
    # Maybe we should work with startTime and stopTime instead? but how?
    # Also we still cannot process multiple segments of same title on the same day.
    # Also some segments can start at the last hour of Sat and pursue next day. We cannot treat those cases yet.
    for key, startTime in enumerate(reversedHHMMList):
      rowspanDict[startTime] = {}
      for Day in DayList:
        # title should be renamed "segment", really.
        title = jsonSchedule[startTime][Day]
        classChunkExist = ''
        plays = ''
        texts = ''
        segmentImg = ''
        classTooltipPosition = 'tooltipBottomLeft'
        if Day in ['Mon', 'Tue']: classTooltipPosition = 'tooltipBottomRight'
        info("Processing: %s %s %s %s" %(key, startTime, Day, title), 2, progress)

        # we need getTextDict to get chunk names for the play buttons, and to build the missing wordClouds
        gettext = "week=%s+title=%s+Day=%s" %(weekNumber, title, Day)
        getTextDict = buildGetTextDict(gettext)

        # without +1, jsonSchedule[reversedHHMMList[key+1]] will error out with IndexError: list index out of range
        # with +1,    we will not process the last startTime == 23:00
        # solution:   create a dumb function for if key+1 < len(reversedHHMMList) == getNextKey
        
        # notByChunk:
        if not byChunk:
          # By default we start with a normal, chunked cell of 30mn:
          # Also we should not have to filter by week anymore since version 0.9.6 
          # , we generate both html and png under each ./week subfolder
          regexp = re.compile(".*KJZZ week=%s.*title=%s.*Day=%s" %(weekNumber, title, Day))
          
          # 1. Is it in the list we build at the beginning?
          thatWordCloudPngList = list(filter(regexp.match, pngList))
          # 2. Was it generated at some point?
          #    Remember, we process every startTime in reversedHHMMList, so we may have already generated it
          if len(thatWordCloudPngList) == 0:
            thisPngPath = '%s/KJZZ week=%s title=%s Day=%s*.png' %(os.path.join(outputFolder, str(weekNumber)), weekNumber, title, Day)
            thatWordCloudPngList = glob.glob(thisPngPath, recursive=False)

          # now we are certain that we need to generate the wordCloud
          # Note: there is a bug when using force: since we process by HHMMList, we may regenerate same segments multiple times
          if len(thatWordCloudPngList) == 0 or force:
            # setup an empty src for an img is indeed an error we will get the missingCloud.png for:
            thatWordCloudPngList = []
            
            # we will not bother looking for excluded programs such as Jazz Blues etc:
            if not any(word in title for word in listTitleWords2Exclude):
              records = getChunks(getTextDict, True, progress)
              # records = [('2023-10-14 01:00:00.000', '2023-10-14 01:30:00.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...'),..]
              # each record is a 30mn chunk of a segment
              if len(records) > 0:
                wordCloudTitle = "KJZZ " + gettext.replace("+", " ")
                # we only print info if we actually generate the wordCloud as i t takes time:
                if autoGenerate: info('Generate wordCloud "%s" ...' %(wordCloudTitle), 1, progress)
                                  # genWordClouds(records, title, mergeRecords, showPicture, wordCloudDict, outputFolder=outputFolder, dryRun=False, progress="")
                genWordCloudDicts = genWordClouds(records, wordCloudTitle, True, showPicture, wordCloudDict, os.path.join(outputFolder, str(weekNumber)), not autoGenerate, progress)
                # we should only have 1 item since we mergeRecords
                if len(genWordCloudDicts) > 0:
                  classChunkExist = 'class="chunkExist"'
                  thatWordCloudPngList = [os.path.basename(genWordCloudDicts[0]["outputFileName"])]
              # else:
                # # we do not have any record in the db, no use to show a missing image
                # thatWordCloudPngList = [voidPic]
            # else:
              # # no use to show a missing image for musical programs
              # thatWordCloudPngList = [voidPic]
          else:
            # all images are inside the html week's folder
            classChunkExist = 'class="chunkExist"'
            thatWordCloudPngList = [os.path.basename(thatWordCloudPngList[0])]

          if len(thatWordCloudPngList) > 0:
            segmentImg = genSegmentImg(thatWordCloudPngList[0], classChunkExist)
            records = getChunks(getTextDict, False, progress)
            # print(getTextDict)
            # print(records)
            # records = [('2023-10-14 01:00:00.000', '2023-10-14 01:30:00.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]'),..]

            # fontawesome incons: https://fontawesome.com/search?m=free&o=r
            for record in records:
              # This is by segment (title), not byChunk: we therefore list all chunks for that segment.
              # Also, no \n between them or it will translate into a white space
              startDict   = TimeDict(record[0])
              stopDict    = TimeDict(record[1])
              chunkName   = record[2]
              misInfoText = record[3]
              plays += genPlayButton(startDict.HHMM, stopDict.HHMM, chunkName, misInfoText, dictHeatMapBlank.keys(), classTooltipPosition, progress)
              texts += genTextButton(chunkName, progress)

          rowspanDict[startTime][Day] = genHtmlChunk(rowspan[Day], classChunkExist, title, plays, texts, segmentImg)

          # if we are not processing the last time key of the day:
          if getNextKey(reversedHHMMList, key):
            info(startTime, 4, progress)
            if title == jsonSchedule[getNextKey(reversedHHMMList, key)][Day]:
              # create a missing td for the rowspan to happen:
              rowspanDict[startTime][Day] = ''
              rowspan[Day] += 1
              info("%s +1 %s %s - %s" %(startTime, rowspan[Day], title, jsonSchedule[getNextKey(reversedHHMMList, key)][Day]), 4, progress)
            else:
              rowspan[Day]  = 1
              info("%s =1 %s %s - %s" %(startTime, rowspan[Day], title, jsonSchedule[getNextKey(reversedHHMMList, key)][Day]), 4, progress)
          
          # if we are processing the last key == 00:00 since we loop in reverse:
          else:
            info("%s =1 %s %s - %s" %(startTime, rowspan[Day], title, None), 4, progress)
        
        # byChunk:
        else:
          if not any(word in title for word in listTitleWords2Exclude):
            listChunks = getChunks(getTextDict, False, progress)
            # listChunks = [
              # ('01:00', '01:30', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]'),
              # ('01:30', '02:00', 'KJZZ_2023-10-14_Sat_0130-0200_BBC World Service', None),
              # ...
            
            # if checkChunk(getTextDict, progress):
            # print(getTextDict)
            # print(listChunks)
            for row in listChunks:
              # Our schedule is by the hour but the db is by chunk of 30mn so we have certainly 2 chunks per hour:
              # And do not forget we process HHMMList in reverse!
              # There is a simple trick to simplify our lives: just compare the hour
              # Also, no \n between them or it will translate into a white space
              if startTime[:2] == row[0][:2]:
                classChunkExist = 'class="chunkExist"'
                plays += genPlayButton(row[0], row[1], row[2], row[3], dictHeatMapBlank.keys(), classTooltipPosition, progress)
                texts += genTextButton(row[2], progress)
          # rowspanDict[startTime][Day] = '<td rowspan="%s" %s><div>%s<span>%s</span><span>%s</span></div></td>\n' %(rowspan[Day], classChunkExist, title, play, texts)
          rowspanDict[startTime][Day] = genHtmlChunk(rowspan[Day], classChunkExist, title, plays, texts)
          info("%s =1 %s %s - %s" %(startTime, rowspan[Day], title, None), 4, progress)
      
        progress.advance(task)
  
  info(rowspanDict, 4, progress)
  for startTime in HHMMList:
    # html += '    <tr><td>00:00</td><td>BBC World Service</td><td>Classic Jazz with Chazz Rayburn</td><td>Classic Jazz with Bryan Houston</td><td>Classic Jazz with Bryan Houston</td><td>Classic Jazz with Michele Robins</td><td>Classic Jazz with Michele Robins</td><td>BBC World Service</td></tr>'
    info('    <tr><td>%s</td>'           %(startTime), 4, progress)
    html   += '    <tr><td class="startTime">%s</td>'           %(startTime)
    
    for Day in DayList:
      html   +=     '%s'  %(rowspanDict[startTime][Day])
    html   +=     '</tr>\n'
  
  html += '</tbody>\n'
  html += '</table>\n'

  # https://github.com/openplayerjs/openplayerjs/blob/master/docs/
  # for simplicity of switching tracks when you click play buttons, 
  # track is pre-added so we can find it with a simple document.querySelector("track").track
  html += '''
<div class="audio">
  <audio id="player" class="op-player__media">
    <track kind="subtitles" srclang="en" label="English" />
  </audio>
</div>\n'''
  # <source src="KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.mp3" type="audio/mp3" />
  # <track src="KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.vtt" kind="subtitles" srclang="en" label="English" />

  html += genHtmlFooter()
  html += '</body>\n'
  html += '</html>'
  
  outputFile = os.path.join(outputFolder, str(weekNumber), outputFileName)
  with open(outputFile, 'w') as fd:
    fd.write(html)
    info("outputFile: %s" %(outputFile), 1, progress)

  return html
# genHtml


def buildGetTextDict(gettext, gettextDict=gettextDict):
  # gettext = "week=43+title=Classic Jazz with Chazz Rayburn+Day=Mon"
  
  if gettext.find("chunk=") > -1:
    chunkName = re.split(r"[=]",gettext)[1]
    # KJZZ_2023-10-13_Fri_1700-1730_All Things Considered
    # we already defined a class that will gently split the name for us
    # python KJZZ-db.py --gettext chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v
    chunk = Chunk(chunkName)
    gettextDict["start"]  = chunk.start
  else:
    conditions = re.split(r"[+]",gettext)
    for condition in conditions:
      key = re.split(r"[=]",condition)[0]
      if key in gettextKeys:
        gettextDict[key] = re.split(r"[=]", condition)[1]
      else:
        error("%s is invalid in %s" %(key, condition), 0)
        info("example: week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\"", 0)
        info("example: chunk=\"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered\"", 0)
        exit(9)
    # for
  #
  return gettextDict  # gettextDict = {'week': '43', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
  # gettextDict = {'week': '43', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
# buildGetTextDict


def error(message, RC=1, progress=""):
  stack = ''
  errorPattern = "error  : %-30s[red]%s%s [/]"
  for i in reversed(range(1, len(inspect.stack())-1)): stack += "%s: " %(inspect.stack()[i][3])
  if progress:
    progress.console.print(errorPattern %(stack, " ", message))
  else:
    print (errorPattern %(stack, " ", message), file=sys.stderr)
  if RC: exit(RC)
#

def warning(message, RC=0, progress=""):
  stack = ''
  warningPattern = "warning: %-30s[yellow]%s%s [/]"
  for i in reversed(range(1, len(inspect.stack())-1)): stack += "%s: " %(inspect.stack()[i][3])
  if progress:
    progress.console.print(warningPattern %(stack, " ", message))
  else:
    print (warningPattern %(stack, " ", message), file=sys.stderr)
  if RC: exit(RC)
#

def info(message, verbosity=0, progress=""):
  stack = ''
  infoPattern = "info   : %s[white]%s%s[/]"
  if verbosity >1:
    for i in reversed(range(1, len(inspect.stack())-1)): stack += "%s: " %(inspect.stack()[i][3])
    infoPattern = f"info   : %-30s[white]%s%s[/]"
    
  # if verbose >= verbosity: print ("info   : %-30s[white]%s%s[/]" %(stack, " ", message), file=sys.stderr)
  if verbose >= verbosity:
    if progress:
      progress.console.print(infoPattern %(stack, " ", message))
    else:
      print (infoPattern %(stack, " ", message), file=sys.stderr)
#

def ddebug(*kwargs):
  print('ddebug',kwargs)
#


def usage(RC=99):
  usage  = (("usage: python %s --help") % (sys.argv[0]))+os.linesep
  usage += ("Required at least: --import / --query / --gettext / --listLevel")+os.linesep
  usage += ("")+os.linesep
  usage += ("  --import < --text \"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered.text\" | --folder inputFolder >")+os.linesep
  usage += ("    -m, --model *%s medium large...\n                   Model that you used with whisper, to transcribe the text to import." %(model))+os.linesep
  usage += ("    -p, --pretty\n                   Convert \\n to carriage returns and convert json ouyput to text.\n                   Ignored when outputing pictures.")+os.linesep
  usage += ("    --output *%s\\\n                   Folder where to output PICtures.\n                   Will be %s\\week\\ when gettext has week=n" %(outputFolder, outputFolder))+os.linesep
  usage += ("    --show\n                   Opens the PICtures upon generation.")+os.linesep
  usage += ("    --rebuildThumbnails <week>\n                   Will (re)generate only PICtures thumbnails for that week, if main PICtures exist.")+os.linesep
  usage += ("    --noPngquant\n                   Disable pngquant compression")+os.linesep
  usage += ("    --useJpeg\n                   Produces jpeg PICtures instead of png.")+os.linesep
  usage += ("    --jpegQuality <*50>\n                   0-100 jpeg quality for PICtures.")+os.linesep
  usage += ("    --dryRun\n                   Will not generate PICtures, will not import or update the database.")+os.linesep
  usage += ("    --noPics\n                   Will not generate PICtures.")+os.linesep
  usage += ("    --force\n                   Will regenerate existing PICtures.")+os.linesep
  usage += ("")+os.linesep
  usage += ("  --db *%s    Path to the local SQlite db." %(localSqlDb))+os.linesep
  usage += ("  -q, --query < title | first | last | last10 | byDay | byTitle | chunkLast10 >\n                   Quick and dirty way to see what's in the db.")+os.linesep
  usage += ("")+os.linesep
  usage += ("  --html [--byChunk --printOut --autoGenerate] <week>\n                   PICture: generate week number's schedule as an html table.")+os.linesep
  usage += ("                   Outputs html file: %s/week00[-byChunk].html" %(outputFolder))+os.linesep
  usage += ("                   --byChunk  Outputs schedule by 30mn chucks, no rowspan, no PICtures.")+os.linesep
  usage += ("                   --printOut Will output html on the prompt.")+os.linesep
  usage += ("                   --autoGenerate Will loop generate all wordCloud PICtures to show in html for that week.")+os.linesep
  usage += ("")+os.linesep
  usage += ("  -g, --gettext < selector=value : chunk= | date= | datetime= | week= | Day= | time= | title= >")+os.linesep
  usage += ("                   Outputs all text from the selector:")+os.linesep
  usage += ("                   chunk=\"KJZZ_YYYY-mm-DD_Ddd_HHMM-HHMM_Title\" (run %s -q chunkLast10 to get some values)" % (sys.argv[0]))+os.linesep
  usage += ("                   date=2023-10-08[+time=HH:MM]")+os.linesep
  usage += ("                   datetime=\"2023-10-08 HH:MM\"")+os.linesep
  usage += ("                   week=42 (iso week with Mon first)")+os.linesep
  usage += ("                   Day=Fri (Ddd)")+os.linesep
  usage += ("                   title=\"title of the show\", see https://kjzz.org/kjzz-print-schedule")+os.linesep
  usage += ("          example: chunk=\"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered\"\n                   Will get text from that chunk of programming only. Chunks are 30mn long.")+os.linesep
  usage += ("          example: week=41+Day=Fri+title=\"All Things Considered\"\n                   Same as above but will get text from the entire episode.")+os.linesep
  usage += ("   *--printOut\n                   Will output selected text on the prompt (default if no other option passed).")+os.linesep
  usage += ("    --noMerge\n                   Do not merge 30mn chunks of the same title within the same timeframe.")+os.linesep
  usage += ("    --misInformation\n                   PICture: generate misInformation graph or heatmap for all 4 factors:\n                   explanatory/retractors/sourcing/uncertainty")+os.linesep
  usage += ("      --graphs *bar,*pie,line \n                   What graph(s) you want. Ignored with --noMerge: a heatMap will be generated instead.")+os.linesep
  usage += ("    --wordCloud\n                   PICture: generate word cloud from gettext output. Will not output any text.")+os.linesep
  usage += ("      --stopLevel  0 1 2 *3\n                   Add various levels of stopwords")+os.linesep
  usage += ("        --listLevel <0[,1,..]> to just show the stopWords in that level(s).")+os.linesep+os.linesep
  for key, item in wordCloudDict.items():
    if item["input"]: usage += ("      --%s *%s %s" %(key, item["value"], item["usage"]))+os.linesep
  usage += ("")+os.linesep
  usage += ("  -v, --verbose\n                   -vv -vvv increase verbosity.")+os.linesep
  usage += ("  --silent\n                   Not verbose.")+os.linesep
  # usage += ("            --inputStopWordsFiles file.txt (add words from file on top of other levels)")+os.linesep
  # usage += ("            --max_words *4000")+os.linesep
  # usage += ("            --font_path *\"fonts\\Quicksand-Bold.ttf\"")+os.linesep
  # usage += ("       --gettext week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\"")+os.linesep
  
  print(usage)
  exit(RC)
#


####################################### main #######################################
####################################### main #######################################
####################################### main #######################################
# Remove 1st argument which is the script itself
argumentList = sys.argv[1:]
# define short Options
options = "hviq:g:d:t:f:m:p"
# define Long options
long_options = ["help", "verbose", "import", "text=", "db=", "folder=", "model=", "query=", "pretty", "gettext=", "wordCloud", "noMerge", "keepStopwords", "stopLevel=", "font_path=", "show", "max_words=", "misInformation", "output=", "graphs=", "html=", "byChunk", "printOut", "listLevel=", "silent", "noPics", "dryRun", "autoGenerate", "rebuildThumbnails=", "noPngquant", "useJpeg", "jpegQuality=", "force"]
wordCloudDictToParams = [(lambda x: '--' + x)(x) for x in wordCloudDict.keys()]
wordCloudDictToOptions = [(lambda x: x + '=')(x) for x in wordCloudDict.keys()]
long_options += wordCloudDictToOptions

try:
  # Parsing argument
  arguments, values = getopt.getopt(argumentList, options, long_options)
  # print (arguments) # [('-f', '41'), ('--model', 'small'), ('--verbose', ''), ('-h', '')]
  # print (values)    # []

  # checking critical arguments
  for currentArgument, currentValue in arguments:
    if currentArgument in ("-h", "--help"):
      usage(0)
    elif currentArgument in ("-v", "--verbose"):
      if not silent: verbose += 1
    elif currentArgument in ("--silent"):
      silent = True
      verbose  = -1

  # checking each argument
  info(("[bright_black]%-20s:[/] %s") % ('argument', 'value'), 2)
  info(("[bright_black]%-20s:[/] %s") % ('----------------', '----------------'), 2)
  for currentArgument, currentValue in arguments:
    currentArgumentClean = currentArgument.replace('-','')
    
    # IMPORT
    if currentArgument in ("-i", "--import"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      importChunks = True
      
    # QUERY THE DB
    elif currentArgument in ("-q", "--query"):
      if currentValue in ("last10","10"):
        sqlQuery = sqlListLast10text
      elif currentValue in ("last"):
        sqlQuery = sqlLastText
      elif currentValue in ("first"):
        sqlQuery = sqlFirstText
      elif currentValue in ("Day","byDay"):
        sqlQuery = sqlCountsByDay
      elif currentValue in ("title"):
        sqlQuery = sqlTitles
      elif currentValue in ("byTitle"):
        sqlQuery = sqlCountsByTitle
      elif currentValue in ("chunkLast10","chunksLast10"):
        sqlQuery = sqlListChunksLast10
      else:
        sqlQuery = currentValue
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
    
    # OUTPUT and PROCESS STUFF
    elif currentArgument in ("-g", "--gettext"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      gettext = currentValue
      if not gettext:
        error("gettext takes an argument: the program to get the text from!", 0)
        info("example: week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\"", 0)
        info("example: chunk=\"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered\" (mutually exclusive to the others)", 0)
        exit(8)

    elif currentArgument in ("-p", "--pretty"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      pretty = True
    elif currentArgument in ("--noMerge"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, False), 2)
      mergeRecords = False
    elif currentArgument in ("--keepStopwords"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, False), 2)
      removeStopwords = False
    elif currentArgument in ("--show"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      showPicture = True
    elif currentArgument in ("--force"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      force = True
    elif currentArgument in ("--stopLevel"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      stopLevel = int(currentValue)
    elif currentArgument in ("-t", "--text"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      inputTextFile = Path(currentValue)
    elif currentArgument in ("-d", "--db"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      localSqlDb = Path(currentValue)
    elif currentArgument in ("-f", "--folder"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      inputFolder = Path(currentValue)
    elif currentArgument in ("--output"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      outputFolder = Path(currentValue)
    elif currentArgument in ("-m", "--model"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      model = currentValue
    elif currentArgument in ("--graphs"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      graphs = currentValue.split(',')
    elif currentArgument in ("--html"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      weekNumber = int(currentValue)
    elif currentArgument in ("--jpegQuality"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      jpegQuality = int(currentValue)
    elif currentArgument in ("--byChunk"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      byChunk = True
    elif currentArgument in ("--printOut"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      printOut = True
    elif currentArgument in ("--noPics"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      noPics = True
    elif currentArgument in ("--dryRun"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      dryRun = True
      noPics = True
    elif currentArgument in ("--autoGenerate"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      autoGenerate = True
    elif currentArgument in ("--listLevel"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      listLevel = currentValue.split(',')
    elif currentArgument in ("--rebuildThumbnails"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      rebuildThumbnail = True
      weekNumber = int(currentValue)
    elif currentArgument in ("--silent"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      silent = True
      verbose = -1
    elif currentArgument in ("--wordCloud"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      wordCloud = True
      misInformation = False
    elif currentArgument in ("--noPngquant"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, False), 2)
      usePngquant = False
    elif currentArgument in ("--useJpeg"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      useJpeg = True
      usePngquant = False
    elif currentArgument in ("--misInformation"):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, True), 2)
      wordCloud = False
      misInformation = True

      # wget https://raw.githubusercontent.com/PDXBek/Misinformation/master/lists/explanatory.csv -O heatMap.explanatory.csv
      # wget https://raw.githubusercontent.com/PDXBek/Misinformation/master/lists/retractors.csv  -O heatMap.retractors.csv
      # wget https://raw.githubusercontent.com/PDXBek/Misinformation/master/lists/sourcing.csv    -O heatMap.sourcing.csv
      # wget https://raw.githubusercontent.com/PDXBek/Misinformation/master/lists/uncertainty.csv -O heatMap.uncertainty.csv
    
    # now processing any values from wordCloudDict that are valid inputs
    elif (currentArgument in (wordCloudDictToParams) and wordCloudDict[currentArgumentClean]["input"]):
      info(("[bright_black]%-20s:[/] %s") % (currentArgumentClean, currentValue), 2)
      if isinstance(wordCloudDict[currentArgumentClean]["default"],int):    wordCloudDict[currentArgumentClean]["value"] = int(currentValue)
      if isinstance(wordCloudDict[currentArgumentClean]["default"],float):  wordCloudDict[currentArgumentClean]["value"] = float(currentValue)
      if isinstance(wordCloudDict[currentArgumentClean]["default"],list):   wordCloudDict[currentArgumentClean]["value"].append(currentValue)
      if isinstance(wordCloudDict[currentArgumentClean]["default"],str):    wordCloudDict[currentArgumentClean]["value"] = currentValue
except getopt.error as err:
  # output error, and return with an error code
  error(err, 3)
#


####################################### MANDATORIES #######################################
if (not importChunks and not sqlQuery and not gettext and not weekNumber and not listLevel):
  error("must pass at least --import / --query / --gettext / --listLevel", 10)
####################################### MANDATORIES #######################################



#################################### help functions
if listLevel:
  stopwordsDict = loadStopWordsDict()
  if pretty:
    for level in listLevel: print(('%s') %(" ".join(stopwordsDict[int(level)])))
  else:
    print("stopwords levels: %s" %(stopwordsDict.keys()))
    for level in listLevel: print("%s" %(stopwordsDict[int(level)]))
  exit()
#

if rebuildThumbnail:
  rebuildThumbnails(os.path.join(outputFolder, str(weekNumber)), os.path.join(outputFolder, str(weekNumber)), dryRun)
  exit()

def importInputStopWords(wordCloudDict):
  if wordCloudDict["inputStopWordsFiles"]["value"]:
    for inputStopWordsFile in wordCloudDict["inputStopWordsFiles"]["value"]:
      with open(inputStopWordsFile, 'r') as fd:
        for line in fd:
          wordCloudDict["inputStopWords"]["value"].append(line.strip())
      info("%s stopWords imported from '%s'" %(len(wordCloudDict["inputStopWords"]["value"]), inputStopWordsFile), 2)
    #
  #
  return wordCloudDict
# importInputStopWords

wordCloudDict = importInputStopWords(wordCloudDict)

#################################### help functions



#################################### db init
if localSqlDb:
  info("localSqlDb: %s" % (os.path.realpath(localSqlDb)), 1)
  if (not os.path.isfile(localSqlDb) or os.path.getsize(localSqlDb) == 0):
    info(("localSqlDb: %s is empty") % (localSqlDb), 1)
    # localSqlDb.unlink()
    conn = db_init(localSqlDb)
  else:
    conn = db_init(localSqlDb)
  if (not os.path.isfile(localSqlDb) or os.path.getsize(localSqlDb) == 0):
    error("localSqlDb %s could not be created" % (os.path.realpath(localSqlDb)), 5)
else:
  error('localSqlDb undefined', 6)
#
#################################### db init



#################################### import of new chunks of broadcast
if importChunks:
  if (not inputTextFile and not inputFolder):
    error("--import requires --text <file.text> or --folder <folder>", 10)

  # first we build inputFiles
  if inputTextFile:
    inputFiles += readInputFile(inputTextFile)
  if inputFolder:
    inputFiles += readInputFolder(inputFolder)
  
  # second we load the db with inputFiles
  if len(inputFiles):
    db_load(inputFiles, localSqlDb, conn, model, True)
    
    # finally we will also print a summary:
    info("python KJZZ-db.py -q title", 2)
    if verbose >2: sqlQuery = sqlCountsByTitle
  else:
    error('No files found to import', 7)
# importChunks
#################################### import of new chunks of broadcast



#################################### sqlQuery
# sometimes a query can be set after an import. 
# Therefore, execute query comes after.
#
# python KJZZ-db.py -q chunkLast10 -v -p
#
if sqlQuery: sqlQueryPrintExec(sqlQuery, pretty)

# records = [('2023-10-16 03:00:00.000', "Hi, I'm Phil Latspin..."), ...]
#################################### sqlQuery



#################################### genHtml
if weekNumber:
  html = genHtml(jsonScheduleFile, outputFolder, weekNumber, byChunk)
  # also generate the other one but do not return its value
  genHtml(jsonScheduleFile, outputFolder, weekNumber, not byChunk)

  if printOut: print(html)
# weekNumber:
#################################### genHtml


# python KJZZ-db.py -g chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v -p
#################################### gettext
if gettext:

  ################### Process inputStopWordsFiles if any:
  # gettext = "week=43+title=Classic Jazz with Chazz Rayburn+Day=Mon"
  # gettextDict = {'week': '43', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
  gettextDict = buildGetTextDict(gettext)
  wordCloudTitle = "KJZZ " + gettext.replace("+", " ")
  
  records = getChunks(gettextDict, True, progress)
  # records = (('2023-10-14 01:00.000', '2023-10-14 01:30.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...'),..)
  
  if len(records) > 0:

    ################## wordCloud
    # first we check if week number was passed in the gettext to infer outputFolder
    if "week" in gettextDict: outputFolder = os.path.join(outputFolder, str(gettextDict['week']))
    # then we check if a wordCloud is requested:
    if wordCloud:
      genWordCloudDicts = genWordClouds(records, wordCloudTitle, mergeRecords, showPicture, wordCloudDict, outputFolder, dryRun)

    ################## misInformation
    # then we check if a misInformation is requested:
    elif misInformation:
      genMisinfoDicts = genMisInformation(records, mergeRecords, wordCloudTitle, graphs, showPicture, dryRun)

      # now for not mergeRecords, we update the database with those 4 values as text, for each chunk:
      # ddebug(genMisinfoDicts)
      # {
      # 'heatMaps': [
          # [0.7, 0.4, 0.4, 2.9],
          # ..
          # [0.4, 0.4, 0.3, 2.3]
        # ],
      # 'Xlabels': ['explanatory', 'retractors', 'sourcing', 'uncertainty'],
      # 'Ylabels': [
          # '03:00',
          # ..
          # '08:30'
        # ]
      # }
      
      # update db if we have results AND not doing mergeRecords
      if not mergeRecords and genMisinfoDicts["heatMaps"]:
        # do not re-update the db if the values were present with getChunks()
        # records = (('2023-10-14 01:00.000', '2023-10-14 01:30.000', 'KJZZ_2023-10-14_Sat_0100-0130_BBC World Service', '[0.7, 0.4, 0.4, 2.9]', 'text...'),..)
        for index, misInfo in enumerate(genMisinfoDicts["heatMaps"]):
          if records[index][3] is None or force:
            # ddebug( ",".join(map(str, misInfo)))
            # start times are unique, why do we bother with other conditions?
                       # gettextDict = {'week': '43', 'title': 'Classic Jazz with Chazz Rayburn', 'Day': 'Mon'}
            # for key in gettextDict: textConditions += "and %s='%s'" %(key, )+ gettextDict[key]
                                                              # textConditions = "and week='..' and title='..' and Day='..'"

            # start times are unique and it's the first column in records, and len(records) == len(genMisinfoDicts["heatMaps"])
            textConditions = "and start='%s'" %(records[index][0])
            # to reload misInfo as an object, simply do json.loads(misInfoText)
            db_update('schedule', 'misInfo', str(misInfo), textConditions, localSqlDb, conn, False)
                                                              # textConditions = "and start='YYYY-MM-DD HH:MM'"
          conn.commit()
  
    # Finally, we just output gettext: printOut is purely optional since it's the last option
    else:
      printOutGetText(records, mergeRecords, pretty, dryRun)
    
  # exit(0)
#
#################################### gettext


# sql = """ SELECT * from schedule where start = '2023-10-08 23:00:00.000'; """

# set ROOT=E:\GPT\stable-diffusion-webui
# call %ROOT%\venv\Scripts\activate
# pushd E:\GPT\KJZZ
# python KJZZ-db.py


exit()
























import regex
text = '''
Hi, I'm Tiara Vaian, KJZ's audio service is supported by 1AZ Credit Union, a locally based credit union giving members
access to a full suite of financial products, including checking accounts, savings accounts and home and auto loans,
more at 1AZCU.com.
Bringing the past to life. This week we're talking about oil and marking 50 years since a global oil crisis.
The era of cheap fuel and cheap energy is over.
We'll hear OPEC's rationale for slashing production in 1973. Plus the oil field that transformed a country.
International oil companies are about to make the biggest foreign investment in Russia since the collapse of communism.
American company Chevron has found oil on a grand scale in the Republic of Kazakhstan in Central Asia.
Also the devastating Amaco Cadiz oil spillage in 1978, the people of the Amazon who took big oil to court and why not
everyone celebrated when black gold was struck in Nigeria.
'''

print (text.lower().count("this"))
print (text.lower().count("warming"))
print (text.lower().count("global warming"))
print (text.lower().count("climate change"))
print (text.lower().count("change"))
words = text.lower().partition("global warming")


# TODO: https://stackoverflow.com/questions/31897436/efficient-way-to-get-words-before-and-after-substring-in-text-python/31932413#31932413
# my question: https://stackoverflow.com/questions/31897436/efficient-way-to-get-words-before-and-after-substring-in-text-python/31932413?noredirect=1#comment136272843_31932413
# answer: @scavenger: What do you mean by "multi-word search" ? Note that the pattern uses the VERBOSE flag, so, If you want to figure several words separated by blank characters, you have to escape them several\ words\ separated\ by\ spaces or to put the searched expression between \Q and \E to quote them for the pattern, like that: \Qseveral words separated by spaces\E, otherwise spaces are ignored. – 

# word = 'global warming'
word = 'warming'
n = 4
pattern = r'''
\m (?<target> %s ) \M # target word
(?<= # content before
    (?<before> (?: (?<wdb>\w+) \W+ ){0,%d} )
    %s
)
(?=  # content after
    (?<after>  (?: \W+ (?<wda>\w+) ){0,%d} )
)
''' % (word, n, word, n)

rgx = regex.compile(pattern, regex.VERBOSE | regex.IGNORECASE)

class Result(object):
    def __init__(self, m):
        self.target_span = m.span()
        self.excerpt_span = (m.starts('before')[0], m.ends('after')[0])
        self.excerpt = m.expandf('{before}{target}{after}')
        self.words_before = m.captures('wdb')[::-1]
        self.words_after = m.captures('wda')


results = [Result(m) for m in rgx.finditer(text)]

if len(results) == 0:
  print(("%s not found in %s") %(word,text))
  exit(1)

len(results)
# 2

print(results[0].excerpt)
# is that this global warming is man-made and
print(results[0].excerpt_span)
# (6236, 6279)
print(results[0].words_before)
# ['is', 'that', 'this', 'global']
print(results[0].words_after)
# ['is', 'man', 'made', 'and']

print(results[1].excerpt)
# the heart of global warming
# but also through the
print(results[1].excerpt_span)
# (26322, 26370)
print(results[1].words_before)
# ['the', 'heart', 'of', 'global']
print(results[1].words_after)
# ['but', 'also', 'through', 'the']
