# author:  AudioscavengeR
# license: GPLv2
# version: 0.9.3

# Identify and challenge bias in language wording, primarily directed at KJZZ's radio broadcast. BiasBuster provides an automated stream downloader, a SQLite database, and Python functions to output visual statistics.
# Will produce:
# - CUDA word transcription from any audio files, based on Whisper-Faster
# - Words cloud, based on amueller/word_cloud
# - Gender bias statistics, based on auroracramer/language-model-bias
# - Misinformation analysis heatmap, based on PDXBek/Misinformation


# https://kjzz.org/kjzz-print-schedule

# python KJZZ-db.py -i -f kjzz\43
# python KJZZ-db.py -q title
# python KJZZ-db.py -q chunks10 -p
# python KJZZ-db.py -g chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v --wordCloud
# python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
# python KJZZ-db.py -g title="All Things Considered" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="All Things Considered" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="BBC Newshour" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="BBC World Business Report" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="BBC World Service" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="Fresh Air" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="Here and Now" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="Marketplace" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="Morning Edition" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g title="The Show" -v --wordCloud --mergeRecords
# python KJZZ-db.py -g week=42+Day=Mon+title="The Show" -v --wordCloud --mergeRecords --stopLevel 2
# python KJZZ-db.py -g week=42+Day=Mon+title="All Things Considered" --wordCloud --mergeRecords --stopLevel 3 --show
# python KJZZ-db.py -g week=42 --wordCloud --mergeRecords --stopLevel 3 --show --max_words=10000
# python KJZZ-db.py -g week=43 --wordCloud --mergeRecords --stopLevel 4 --show --max_words=10000

# egrep -i "trans[gsv]" *text
# egrep -i "\bgay\b|lesb|bisex,transg|queer|gender" *text
# egrep -i "diversity|equity|inclusion" *text

import getopt, sys, os, re, regex, io, time, datetime
from dateutil import parser
from pathlib import Path
import json, urllib, random, sqlite3
# https://github.com/Textualize/rich
from rich import print
from rich.progress import track, Progress

# # example of progress bar:
# with Progress() as progress:
  # task = progress.add_task("twiddling thumbs", total=10)
  # inputFiles = [1,2,3,4,5,6,7,8,9,0]
  # for inputFile in inputFiles:
    # progress.console.print(f"Working on job #{inputFile}")
    # time.sleep(0.2)
    # progress.advance(task)
# exit()

# inputFolder = "E:\\GPT\\KJZZ\\41"
importChunks = False
inputFolder = None
inputFiles = []
inputJsonFile = None
inputTextFile = None
localSqlDb = Path("kjzz.db")
conn = None

model = "small"
sqlQuery = None
verbose = False
debug = False
pretty = False
wordCloud = False
gettext = None
validKeys = ["date", "datetime", "week", "Day", "time", "title", "chunk"]
condDict = {}
mergeRecords = False
mergedText = ""
noStopwords = False
showPicture = False
font_path = "fonts\\Quicksand-Bold.ttf"
stopwords = {
  0: ['what','who','is','as','at','he','the','an','to','in','for','of','or','by','with','on','this','that','be','and','it','its'],
  1: ["NPR",'KJZZ','org',"gift","make","support","sustaining","member","doubled","thank","you","call","news","month","help","give","donation","contribution","please","drive"],
  2: ['say','says',"said",'new','one','re','not','but','are','from','become','still','way','went'],
  3: ["now",'know','will','going','well',"yeah","really","right","think","today","time","thing","things","kind","lot","part","year","show","morning","see","much","want","made","sort","come","day","need","got"],
  4: ["even",'never','always'],
}
stopLevel = 0
# after merging 1+2 to what WordCloud has in its own set, we get this:
# stopwords = {
# 0: ['up', 'ever', 'yourself', 'therefore', 'cannot', 'could', 'new', "they've", 'theirs', "who's", 'u', 'an', 'am', 'get', 're', 'where', 'herself', 'same', 'was', "you'd", 'www', 'some', 'through', 'each', 'himself', 'once', 'me', 'have', 'our', 'this', 'or', "i'm", 'they', "hasn't", 'which', 'why', 'to', "how's", 'can', 'com', 'we', 'did', 'yours', 'the', "we're", 'more', 'shall', 'about', 'are', 'so', "they're", "he'd", 'otherwise', 'below', 'else', 'further', 'has', 'most', 'ours', 'ourselves', "why's", 'a', 'at', "we'd", 'between', "isn't", 'that', 'one', 'since', "doesn't", 'her', 'into', 'k', "couldn't", 'before', "she'd", "wasn't", 'it', "don't", 'during', 'only', 'hers', "when's", "shouldn't", "she's", 'in', 'my', 'no', 'however', 'r', "they'll", 'above', 'if', 'he', 'of', 'how', 'over', 'say', 'whom', "we've", "here's", 'been', "hadn't", 's', 'be', 'these', 'own', 'both', 'doing', 'itself', 'but', 'against', 'ought', 'http', 'nor', "weren't", "he's", 'does', 'i', 'and', "what's", "wouldn't", 'myself', 'just', 'out', "they'd", 'on', 'than', 'hence', 'themselves', 'then', 'very', "we'll", 'she', "it's", "you'll", 'its', 'is', "let's", 'were', "won't", 'what', 'by', "that's", 'again', 'had', 'too', "mustn't", "i've", "there's", 'as', "she'll", 'few', 'being', 'when', "aren't", 'should', "shan't", 'all', 'under', 'your', 'here', 'down', 'with', 'also', 'after', "you're", 'like', 'you', "where's", 'not', 'any', 'him', 'until', "you've", 'says', "didn't", 'such', "i'd", "i'll", 'them', 'do', 'while', "haven't", 'there', 'their', 'who', 'because', "he'll", "can't", 'from', 'having', 'for', 'off', 'other', 'would', 'those', 'yourselves', 'his'],
# }

# https://github.com/amueller/word_cloud/blob/master/wordcloud/wordcloud.py
wordCloudDict = {
  "max_words": 4000,
  "width": 1000,
  "height": 500,
  "background_color": "white",
  "relative_scaling": 0,
  "normalize_plurals": True,
  "min_word_length ": 3,
}

sqlLast10 = """ SELECT * from schedule LIMIT 10 """
sqlLast1  = """ SELECT * from schedule LIMIT 1 """
sqlCountsByDay = """ SELECT Day, title, count(start)
          from schedule 
          GROUP BY Day, title
          ORDER BY Day
          """
# [
  # ('Fri', 'All Things Considered', 5),
  # ('Fri', 'BBC Newshour', 2),
  # ('Fri', 'BBC World Service', 4),
  # ('Fri', 'Here and Now', 4),
  # ('Fri', 'Morning Edition', 12),
  # ('Fri', 'Science Friday', 2),
  # ('Fri', 'The Show', 2),

sqlCountsByTile = """ SELECT title, Day, count(start)
          from schedule 
          GROUP BY title, Day
          ORDER BY title
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
# python KJZZ-db.py -q chunks10 -p
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


class Chunk:
  def __init__(self, inputFile, model=model):
    self.inputFile = Path(inputFile)
    self.model = model
    self.dirname = os.path.dirname(self.inputFile)
    self.basename = os.path.basename(self.inputFile)
    self.stem = Path(self.basename).stem
    self.ext = Path(self.basename).suffix
    self.split = re.split(r"[_-]", self.stem) # ['KJZZ', '2023', '10', '09', 'Mon', '1330', '1400', 'BBC Newshour']
    if len(self.split) != 8:
      raise ValueError("    Chunk: invalid name: %s" % (self.inputFile))
    self.week = datetime.date(int(self.split[1]),int(self.split[2]),int(self.split[3])).isocalendar().week
    self.YYYYMMDD = '-'.join([self.split[1],self.split[2],self.split[3]])
    self.Day = self.split[4]
    # we want YYYY-MM-DD HH:MM:SS.SSS
    self.startTime = ':'.join([self.split[5][:2],self.split[5][2:]]) + ":00.000"
    self.start = ' '.join([self.YYYYMMDD, self.startTime])
    self.stopTime = ':'.join([self.split[6][:2],self.split[6][2:]]) + ":00.000"
    self.stop = ' '.join([self.YYYYMMDD, self.stopTime])
    self.title = self.split[-1]
    # with open(self.inputFile, 'r') as pointer:
    if os.path.isfile(self.inputFile):
      with io.open(self.inputFile, mode="r", encoding="utf-8") as pointer:
        self.text = pointer.read()
        # print(text)
#


def usage(RC=99):
  print (("usage: python %s --help") % (sys.argv[0]))
  print ("       --import [ --text \"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered.text\" | --folder folder]")
  print ("       --db *db.sqlite")
  print ("       --model *small medium..")
  print ("       --query [ last last10 byDay byTitle chunks10 ] (show chunks) or simply \"SELECT xyz from schedule\"")
  print ("       --pretty (apply carriage returns)")
  print ("       --gettext week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\"")
  print ("       --gettext chunk=\"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered\" (run %s -q last10 first, to get some values)" % (sys.argv[0]))
  print ("         --wordCloud [--mergeRecords] [--show] (generate word cloud for gettext output)")
  print ("         --stopLevel *0 1 2 (add various levels of stopwords)")
  print ("         --max_words *4000")
  print ("         --font_path *\"fonts\\Quicksand-Bold.ttf\"")
  # print ("       --misinformation week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\" (misinformation heatmap)")
  exit(RC)
#

# If you use the TEXT storage class to store date and time value, you need to use the ISO8601 string format as follows:
# YYYY-MM-DD HH:MM:SS.SSS
def db_init(localSqlDb):
  if verbose: print(("  db_init %s") % (localSqlDb), file=sys.stderr)
  localSqlDb.touch()
  # localSqlDb.unlink()
  conn = sqlite3.connect(localSqlDb)
  cur = conn.cursor()
  queryInit = """
    CREATE TABLE schedule (
          start     TEXT    PRIMARY KEY
        , stop      TEXT    NOT NULL
        , week      INTEGER
        , day       TEXT    NOT NULL
        , title     TEXT    NOT NULL
        , text      TEXT
        , model     TEXT
        );
    """
  try:
    cur.execute(queryInit)
    print(("[green]  db_init %s: success[/]") % (localSqlDb), file=sys.stderr)
    return conn
  except Exception as error:
    if not str(error).find("already exists"):
      print(("[red]    %s[/]") % (error), file=sys.stderr)
    else:
      records = cursor(localSqlDb, conn, """SELECT count(start) from schedule""")
      print(("[green]  db_init: %s chunks found in %s[/]") % (records[0][0],localSqlDb), file=sys.stderr)
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

def db_load(inputFiles, localSqlDb, conn, model):
  loadedFiles = []
  if inputFiles:
    if verbose: print(("  db_load: %s files") % (len(inputFiles)), file=sys.stderr)
  if not conn:
    conn = sqlite3.connect(localSqlDb)
  
  with Progress() as progress:
    task = progress.add_task("Loading...", total=len(inputFiles))
    # KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.text
    for inputFile in inputFiles:
      if verbose: progress.console.print((f"    db_load: reading %s ...") % (inputFile))
      try:
        chunk = Chunk(inputFile, model)
        if verbose: progress.console.print(("    db_load: Chunk: loaded %s") % (chunk.basename))
        # time.sleep(0.2)
      except Exception as error:
        progress.console.print(("[red]    db_load: Chunk: load error for %s: %s[/]") % (inputFile, error))
        exit(1)
      # check if exist in db:
      sql = """ SELECT * from schedule where start = ?; """
      records = cursor(localSqlDb, conn, sql, (chunk.start,))
      # exit()
      if len(records) == 0:
        # load in db:
        sql = """ INSERT INTO schedule(start, stop , week, Day, title, text, model) VALUES(?,?,?,?,?,?,?); """
        records = cursor(localSqlDb, conn, sql, (chunk.start, chunk.stop , chunk.week, chunk.Day, chunk.title, chunk.text, chunk.model))
        loadedFiles += [inputFile]
        progress.console.print(("[green]    db_load: Chunk added: %s[/]") % (chunk.basename))
      else:
        progress.console.print(("[bright_black]    db_load: Chunk already exist: %s[/]") % (chunk.basename))
      progress.advance(task)
  conn.commit()
  print(("  db_load: done loading %s/%s files") % (len(loadedFiles),len(inputFiles)), file=sys.stderr)
#


def cursor(localSqlDb, conn, sql, data=None):
  if not conn:
    conn = sqlite3.connect(localSqlDb)
  cur = conn.cursor()
  records = []
  try:
    if data:
      if debug: print(("    cursor: cur.execute(%s) ... %s ...") %(sql, data[0]), file=sys.stderr)
      cur.execute(sql, data)
    else:
      if debug: print(("    cursor: cur.execute(%s) ...") %(sql), file=sys.stderr)
      cur.execute(sql)
    records = cur.fetchall()
    if verbose: print("    cursor: %s records" % (len(records)))
  except Exception as error:
    print(("[red]    cursor error: %s[/]") % (error), file=sys.stderr)
  return records
#

def chunk2condDict(chunkName):
  # KJZZ_2023-10-13_Fri_1700-1730_All Things Considered
  # we already defined a class that will gently split the name for us
  chunk = Chunk(chunkName)
  print("ddebug"+chunk.start)
#

####################################### main #######################################
####################################### main #######################################
####################################### main #######################################
# Remove 1st argument which is the script itself
argumentList = sys.argv[1:]
# define short Options
options = "hvd:it:f:m:q:pg:wM"
# define Long options
long_options = ["help", "verbose", "import", "text=", "db=", "folder=", "model=", "query=", "pretty", "gettext=", "wordCloud", "mergeRecords", "noStopwords", "stopLevel=", "font_path=", "show", "max_words="]
try:
  # Parsing argument
  arguments, values = getopt.getopt(argumentList, options, long_options)
  # print (arguments) # [('-f', '41'), ('--model', 'small'), ('--verbose', ''), ('-h', '')]
  # print (values)    # []
  # checking each argument
  for currentArgument, currentValue in arguments:
    if currentArgument in ("-h", "--help"):
      usage()
      exit(99)
    elif currentArgument in ("-v", "--verbose"):
      if verbose: print (("[bright_black]verbose:[/]       %s") % (True))
      verbose = True
    elif currentArgument in ("-q", "--query"):
      if currentValue in ("last10","10"):
        sqlQuery = sqlLast10
      elif currentValue in ("1","last"):
        sqlQuery = sqlLast1
      elif currentValue in ("Day","byDay"):
        sqlQuery = sqlCountsByDay
      elif currentValue in ("title","byTitle"):
        sqlQuery = sqlCountsByTile
      elif currentValue in ("chunks10","chunksLast10"):
        sqlQuery = sqlListChunksLast10
      else:
        sqlQuery = currentValue
      if verbose: print (("[bright_black]query:[/]         %s") % (currentValue))
    elif currentArgument in ("-p", "--pretty"):
      if verbose: print (("[bright_black]pretty:[/]        %s") % (True))
      pretty = True
    elif currentArgument in ("-M", "--mergeRecords"):
      if verbose: print (("[bright_black]merge records:[/] %s") % (True))
      mergeRecords = True
    elif currentArgument in ("-i", "--import"):
      if verbose: print (("[bright_black]import:[/]        %s") % (True))
      importChunks = True
    elif currentArgument in ("--noStopwords"):
      if verbose: print (("[bright_black]noStopwords:[/]   %s") % (True))
      noStopwords = True
    elif currentArgument in ("--show"):
      if verbose: print (("[bright_black]show:[/]          %s") % (True))
      showPicture = True
    elif currentArgument in ("--stopLevel"):
      if verbose: print (("[bright_black]stopLevel:[/]     %s") % (currentValue))
      stopLevel = int(currentValue)
    elif currentArgument in ("-t", "--text"):
      if verbose: print (("[bright_black]inputTextFile:[/] %s") % (currentValue))
      inputTextFile = Path(currentValue)
    elif currentArgument in ("-d", "--db"):
      if verbose: print (("[bright_black]localSqlDb:[/]    %s") % (currentValue))
      localSqlDb = Path(currentValue)
    elif currentArgument in ("-f", "--folder"):
      if verbose: print (("[bright_black]inputFolder:[/]   %s") % (currentValue))
      inputFolder = Path(currentValue)
    elif currentArgument in ("-m", "--model"):
      if verbose: print (("[bright_black]model:[/]         %s") % (currentValue))
      model = currentValue
    elif currentArgument in ("-g", "--gettext"):
      if verbose: print (("[bright_black]gettext:[/]       %s") % (currentValue))
      gettext = currentValue
      if not gettext:
        print("example: week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\"")
        print("example: chunk=\"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered\" (mutually exclusive to the others)")
        usage(1)
      if gettext.find("chunk=") > -1:
        chunkName = re.split(r"[=]",gettext)[1]
        # chunk2condDict(chunkName)
        # KJZZ_2023-10-13_Fri_1700-1730_All Things Considered
        # we already defined a class that will gently split the name for us
        # python KJZZ-db.py --gettext chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v
        chunk = Chunk(chunkName)
        condDict["start"]  = chunk.start
      else:
        conditions = re.split(r"[+]",gettext)
        for condition in conditions:
          key = re.split(r"[=]",condition)[0]
          if key in validKeys:
            condDict[key] = re.split(r"[=]",condition)[1]
          else:
            print(("[red]error: %s is invalid in %s[/]") %(key,condition))
            print("example: week=41[+title=\"BBC Newshour\"] | date=2023-10-08[+time=HH:MM] | datetime=\"2023-10-08 HH:MM\"")
            print("example: chunk=\"KJZZ_2023-10-13_Fri_1700-1730_All Things Considered\"")
            usage(1)
    elif currentArgument in ("-w", "--wordCloud"):
      if verbose: print (("[bright_black]wordCloud:[/]     %s") % (True))
      wordCloud = True
    elif currentArgument in ("--font_path"):
      if verbose: print (("[bright_black]font_path:[/]     %s") % (True))
      font_path = Path(currentValue)
    elif currentArgument in ("--max_words"):
      if verbose: print (("[bright_black]max_words:[/]     %s") % (currentValue))
      wordCloudDict["max_words"] = int(currentValue)
except getopt.error as err:
  # output error, and return with an error code
  print(("[red]%s[/]") % (err), file=sys.stderr)
  usage(1)


if (not importChunks and not sqlQuery and not gettext):
  print ("[red]error: must pass at least --import + [ --text / --folder ] or --query or --gettext[/]")
  usage(1)
#


if (localSqlDb):
  if verbose: print(("localSqlDb %s passed") % (localSqlDb))
  if (not os.path.isfile(localSqlDb) or os.path.getsize(localSqlDb) == 0):
    print(("localSqlDb %s is empty") % (localSqlDb))
    # localSqlDb.unlink()
    conn = db_init(localSqlDb)
  else:
    conn = db_init(localSqlDb)
else:
  print ("[red]error: localSqlDb undefined[/]")
  usage(1)
#


if importChunks:
  if inputTextFile:
    if os.path.isfile(inputTextFile):
      if verbose: print(("inputTextFile %s passed") % (inputTextFile))
      inputFiles += inputTextFile
    else:
      if verbose: print("[red]%s not found[/]" % (inputTextFile))
    #
  #
  if inputFolder:
    if os.path.isdir(inputFolder):
      if verbose: print(("  listing folder %s ...") % (inputFolder))
      # inputFiles = sorted([os.fsdecode(file) for file in os.listdir(inputFolder) if os.fsdecode(file).endswith(".text")])
      # inputFiles = sorted([os.path.join(inputFolder, file) for file in os.listdir(inputFolder) if os.fsdecode(file).endswith(".text")] , key=os.path.getctime)
      inputFiles = [str(child.resolve()) for child in Path.iterdir(Path(inputFolder)) if os.fsdecode(child).endswith(".text")]
      for inputFile in inputFiles:
        if (os.path.getsize(inputFile) == 0):
          if verbose: print(("    %s is empty") % (inputFile))
          inputFiles.remove(inputFile)
        # else:
          # print(("    reading %s ...") % (inputFile))
          # with open(inputFile, 'r') as pointer:
            # text = pointer.read()
            # print(text)
      # print(("  %s") % (inputFiles))
      db_load(inputFiles, localSqlDb, conn, model)
      # we will also print a summary
      sqlQuery = sqlCountsByTile
    else:
      if verbose: print("[red]%s not found[/]" % (inputFolder))
      exit(0)
    #
  #
elif (inputTextFile or inputFolder):
  usage(1)
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


# python KJZZ-db.py -q chunks10 -v -p
if sqlQuery:
  if verbose: print("  execute %s" % (sqlQuery))
  records = cursor(localSqlDb, conn, sqlQuery)
  # SQLite: %w = day of week 0-6 with Sunday==0
  # But we want Mon Tue etc so we replace text in each tuple.
  # Oh yeah, sqlite3 fetchall returns a list of tuples.
  # Each record is a tuple: ('KJZZ_2023-10-13_5_1630-1700_All Things Considered',),
  if sqlQuery.find('_%w_') > -1:
    # replaceNum2Days will output the same format: list of tuples
    # What we should do is grab the recursive replace function I wrote 10 years ago, pfff where is it
    records = [replaceNum2Days(record) for record in records]
    # records[0] = map(lambda x: str.replace(x, "[br]", "<br/>"), records[0])
  if pretty:
    for record in records:
      print(('"%s"') %(record))
  else:
    print(records)
  exit(0)
#


def genWordCloud(text, title, noStopwords=False, level=0, wordCloudDict=wordCloudDict):
  # https://github.com/amueller/word_cloud/blob/main/examples/simple.py
  from collections import Counter
  stopWords = title.split()
  
  wordsList = text.split()
  numWords = len(wordsList)
  title = "%s words=%s max=%s scale=%s" % (title, numWords, wordCloudDict["max_words"], wordCloudDict["relative_scaling"])
  fileName = title.replace(": ", "=").replace(":", "")
  
  if not noStopwords:
    for i in range(level + 1): stopWords += stopwords[i]
    # print(len(STOPWORDS))
    STOPWORDS.update(stopWords)
    # print(len(STOPWORDS))
    # print(len(stopWords))
    # print(stopWords)
    # WordCloud can remove stopWords by itself just fine, but we do it just have a count
    if verbose: print("    genWordCloud: most 10 common words before: %s" % (Counter(wordsList).most_common(10)))
    cleanWordsList = [word for word in re.split("\W+",text) if word.lower() not in stopWords]
    if verbose: print("    genWordCloud: most 10 common words after:  %s" % (Counter(cleanWordsList).most_common(10)))
    if verbose: print("    genWordCloud: %s words - %s stopWords == %s total words (%s words removed)" %(numWords,len(STOPWORDS),len(cleanWordsList),numWords - len(cleanWordsList)))
    if verbose: print("    genWordCloud: stopWords = %s" %(str(STOPWORDS)))
  else:
    if verbose: print("    genWordCloud: %s words" %(numWords))
  # image 1: Display the generated image:
  # font_path="fonts\\Quicksand-Regular.ttf"
  wordcloud = WordCloud(
                        stopwords=STOPWORDS, 
                        background_color=wordCloudDict["background_color"], 
                        max_words=wordCloudDict["max_words"], 
                        width=wordCloudDict["width"], 
                        height=wordCloudDict["height"], 
                        relative_scaling=wordCloudDict["relative_scaling"], 
                        normalize_plurals=wordCloudDict["normalize_plurals"], 
                        min_word_length=3,
                        min_font_size=4,
                        font_path=font_path,
                        scale=2,
                        ).generate(text)
  # wordcloud.generate_from_frequencies(Counter(cleanWordsList))
    
  # # trying to save image + add legend 1
  # plt.figure()
  # plt.imshow(wordcloud, interpolation='bilinear')
  # plt.axis("off")
  # # plt.switch_backend('Agg')
  # # plt.savefig(title + ".png")

  # # trying to save image + add legend 2
  # fig, ax = plt.subplots()
  # ax.imshow(wordcloud, interpolation='bilinear')
  # ax.axis("off")
  # # plt.switch_backend('Agg')
  # fig.savefig(title + ".png")
  # plt.title(title)
  # # supported values are 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
  # # plt.legend(loc='best', fancybox=True, shadow=True)    # does not show in saved file
  # # fig.legend(fancybox=True, shadow=True)

  # trying to save image + add legend 3 - that one works
  # plt.subplots(figsize=(8, 4))  # 800 x 400
  plt.subplots(figsize=(20, 10))  # 2000 x 1000
  plt.title(title)
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
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.savefig(fileName  + ".png", bbox_inches='tight')
  print("    genWordCloud: file = \"%s.png\"" % (fileName))


  # # image 2: lower max_font_size
  # wordcloud = WordCloud(max_font_size=40).generate(text)
  # plt.figure()
  # plt.imshow(wordcloud, interpolation="bilinear")
  # plt.axis("off")
  
  # plt.show()

  # The pil way (if you don't have matplotlib)
  # image = wordcloud.to_image()
  # image.show()


# python KJZZ-db.py -g chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v -p
if gettext:
  sqlGettext = "SELECT text from schedule where 1=1"
  title = "KJZZ"
  
  for key in condDict.keys():
    sqlGettext += (" and %s = '%s'" % (key,condDict[key]))
    # reformat start time for the filename:
    if key == "start":
      condDict[key] = parser.parse(chunk.start).strftime("%Y-%m-%d %H:%M")
    title += " %s=%s" % (key,condDict[key])
  if verbose: print("  gettext: %s" %(sqlGettext))
  records = cursor(localSqlDb, conn, sqlGettext)
  if len(records) == 0:
    if verbose: print("  gettext: 0 records for %s" %(condDict))
    exit(0)
  
  # python KJZZ-db.py -g chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v -wordCloud
  # python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
  # python KJZZ-db.py -g title="All Things Considered" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="All Things Considered" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="BBC Newshour" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="BBC World Business Report" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="BBC World Service" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="Fresh Air" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="Here and Now" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="Marketplace" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="Morning Edition" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="The Show" -v --wordCloud --mergeRecords
  # python KJZZ-db.py -g title="Fresh Air"+week=41 -v --wordCloud --mergeRecords
  if wordCloud:
    from wordcloud import WordCloud
    from wordcloud import STOPWORDS
    # print(STOPWORDS)
    import matplotlib
    import matplotlib.pyplot as plt
    
    if mergeRecords:
      for record in records: mergedText += record[0]
      genWordCloud(mergedText, title, noStopwords, stopLevel, wordCloudDict)
    else:
      i = 1
      for record in records:
        if verbose: print("  gettext: image %s" % (i))
        if debug:   print("  gettext: record = \n %s" %(record))
        genWordCloud(record[0], title, noStopwords, stopLevel, wordCloudDict)
      i += 1
    if showPicture: plt.show()
  
  else:
    if pretty:
      for record in records:
        print(('"%s"') %(record))
    else:
      print(records)
  exit(0)
#



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


# https://stackoverflow.com/questions/31897436/efficient-way-to-get-words-before-and-after-substring-in-text-python/31932413#31932413
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
