https://kjzz.org/sites/all/services/kjzzstreamer.php
https://kjzz.org/program-schedule
https://kjzz.org/kjzz-print-schedule

https://kjzz.streamguys1.com/kjzz_mp3_128

await fetch("https://kjzz.streamguys1.com/kjzz_mp3_128", {
    "credentials": "omit",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
        "Accept-Language": "en-US,en;q=0.5",
        "Range": "bytes=261876-",
        "Sec-Fetch-Dest": "audio",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site"
    },
    "method": "GET",
    "mode": "cors"
});

curl "https://kjzz.streamguys1.com/kjzz_mp3_128" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0" -H "Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5" -H "Accept-Language: en-US,en;q=0.5" -H "Range: bytes=261876-" -H "DNT: 1" -H "Connection: keep-alive" -H "Sec-Fetch-Dest: audio" -H "Sec-Fetch-Mode: no-cors" -H "Sec-Fetch-Site: cross-site" -H "Accept-Encoding: identity" >bbb.mp3
busybox timeout 1h curl "https://kjzz.streamguys1.com/kjzz_mp3_128" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0" -H "Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5" -H "Accept-Language: en-US,en;q=0.5" -H "Range: bytes=261876-" -H "DNT: 1" -H "Connection: keep-alive" -H "Sec-Fetch-Dest: audio" -H "Sec-Fetch-Mode: no-cors" -H "Sec-Fetch-Site: cross-site" -H "Accept-Encoding: identity" >bbb.mp3

# https://stackoverflow.com/questions/27595758/linux-date-command-finding-seconds-to-next-hour
epoch=$(date +%s)
date -d@$epoch
# Sat 07 Oct 2023 02:49:30 PM MST
secSinceLastHour=$(( $epoch % 3600 ))
secSinceLastHalf=$(( $epoch % 1800 ))
secUntilNextHour=$(( 3600 - $epoch % 3600 ))
secUntilNextHalf=$(( 1800 - $epoch % 1800 ))
echo $secSinceLastHour $secSinceLastHalf $secUntilNextHour $secUntilNextHalf
# 2816 1016 784 784

epoch=$(date +%s)
date -d@$epoch
# Sat 07 Oct 2023 09:03:02 PM MST
export secSinceLastHour=$(( $epoch % 3600 ))
export secSinceLastHalf=$(( $epoch % 1800 ))
export secUntilNextHour=$(( 3600 - $epoch % 3600 ))
export secUntilNextHalf=$(( 1800 - $epoch % 1800 ))
echo $secSinceLastHour $secSinceLastHalf $secUntilNextHalf $secUntilNextHour
# 182 182 1618 3418

export curHHMM=$(date -d"@$epoch" "+%H:%M")
echo $epoch $curHHMM
# 1696737782 21:03
export epochPrevHalf=$(($epoch - ($epoch % (30 * 60))))
export epochPrevHour=$(($epoch - ($epoch % (60 * 60))))
export epochNextHalf=$(($epoch - ($epoch % (30 * 60)) + 1800))
export epochNextHour=$(($epoch - ($epoch % (60 * 60)) + 3600))
date -d"@$epochPrevHalf"
# Sat 07 Oct 2023 09:00:00 PM MST
date -d"@$epochPrevHour"
# Sat 07 Oct 2023 09:00:00 PM MST
date -d"@$epochNextHalf"
# Sat 07 Oct 2023 09:30:00 PM MST
date -d"@$epochNextHour"
# Sat 07 Oct 2023 10:00:00 PM MST
echo $epochPrevHour $epochPrevHalf
# 1696737600 1696737600
export prevHalfHHMM=$(date -d"@$epochPrevHalf" "+%H:%M")
export prevHourHHMM=$(date -d"@$epochPrevHour" "+%H:%M")
export nextHalfHHMM=$(date -d"@$epochNextHalf" "+%H:%M")
export nextHourHHMM=$(date -d"@$epochNextHour" "+%H:%M")
echo $prevHalfHHMM $prevHourHHMM $nextHalfHHMM $nextHourHHMM
# 21:30 21:00 22:00 22:00
export curDay=$(date -d"@$epochPrevHalf" "+%a")
export curday=$(date -d"@$epochPrevHalf" "+%d")
echo $curDay $curday
# Sat 07
export curweek=$(date -d"@$epochPrevHalf" "+%U")
export curMon=$(date -d"@$epochPrevHalf" "+%b")
export curmon=$(date -d"@$epochPrevHalf" "+%m")
echo $curweek $curMon $curmon
# 40 Oct 10

vi KJZZ-schedule.json
{
  "17:00": {}
  "18:00": {
    "Mon": "Marketplace",
    "Tue": "Marketplace",
    "Wed": "Marketplace",
    "Thu": "Marketplace",
    "Fri": "Marketplace",
    "Sat": "Live Wire",
    "Sun": "Those Lowdown Blues with Bob Corritore"
  },
  "18:30": {
    "Mon": "BBC World Business Report",
    "Tue": "BBC World Business Report",
    "Wed": "BBC World Business Report",
    "Thu": "BBC World Business Report",
    "Fri": "BBC World Business Report",
    "Sat": "Live Wire",
    "Sun": "Those Lowdown Blues with Bob Corritore"
  },
  "19:00": {
    "Mon": "Fresh Air",
    "Tue": "Fresh Air",
    "Wed": "Fresh Air",
    "Thu": "Fresh Air",
    "Fri": "Fresh Air",
    "Sat": "Bullseye",
    "Sun": "Those Lowdown Blues with Bob Corritore"
  },
  "20:00": {}
...

# goal:
any time script runs, must return
- file name with date
- how long it should run in mn

echo $TZ
# America/Phoenix

date
# Sat 07 Oct 2023 12:20:00 PM MST   --> should return:
- name = KJZZ_2023-10-07_12:00-12:30_Here and Now.mp3
- duration = 600
- name = KJZZ_2023-10-07_12:30-13:00_Here and Now.mp3
- duration = 1800

# 1. return current time rounded and Day at 12:35
export prevHalfHHMM=$(date -d"@$epochPrevHalf" "+%H:%M")
export prevHourHHMM=$(date -d"@$epochPrevHour" "+%H:%M")
export nextHalfHHMM=$(date -d"@$epochNextHalf" "+%H:%M")
export nextHourHHMM=$(date -d"@$epochNextHour" "+%H:%M")
echo $prevHalfHHMM $prevHourHHMM $nextHalfHHMM $nextHourHHMM
  # 12:35 # 12:30 12:00
  # 21:33 # 21:30 21:00 22:00 22:00

# 2. return current Day
export curDay=$(date -d"@$epochPrevHalf" "+%a")
  # Sat

# 3. get schedule name for the next 30mn at 12:12
jq -r '."12:00".Sat' KJZZ-schedule.json
  # Code Switch and Life Kit
jq -r '."\($ENV.prevHalfHHMM)"."\($ENV.curDay)"' KJZZ-schedule.json
  # null
jq -r '."\($ENV.prevHourHHMM)"."\($ENV.curDay)"' KJZZ-schedule.json
  # Code Switch and Life Kit
schedule=$(jq -r '."\($ENV.prevHalfHHMM)"."\($ENV.curDay)"' KJZZ-schedule.json)
  # null
schedule=$(jq -r '."\($ENV.prevHourHHMM)"."\($ENV.curDay)"' KJZZ-schedule.json)
  # "Code Switch and Life Kit"

date -d@$epoch
# Sat 07 Oct 2023 09:03:02 PM MST
schedule=$(jq -r '."\($ENV.prevHalfHHMM)"."\($ENV.curDay)"' KJZZ-schedule.json)
[ "$schedule" == "null" ] && schedule=$(jq -r '."\($ENV.prevHourHHMM)"."\($ENV.curDay)"' KJZZ-schedule.json)
echo $schedule
  # Climate One



# 4. gather all that's needed
epoch=$(date +%s)
scheduler() {
  # date
  local allexport=true; set -a
  epoch=$(date +%s)
  jsonSchedule=/docker/kjzz/KJZZ-schedule.json
  (($# > 0)) && jsonSchedule=$1
  (($# > 1)) && epoch=$2
  curHHMM=$(date -d"@$epoch" "+%H:%M")
  secSinceLastHour=$(( $epoch % 3600 ))
  secSinceLastHalf=$(( $epoch % 1800 ))
  secUntilNextHour=$(( 3600 - $epoch % 3600 ))
  secUntilNextHalf=$(( 1800 - $epoch % 1800 ))
  epochPrevHalf=$(($epoch - ($epoch % (30 * 60))))
  epochPrevHour=$(($epoch - ($epoch % (60 * 60))))
  epochNextHalf=$(($epoch - ($epoch % (30 * 60)) + 1800))
  epochNextHour=$(($epoch - ($epoch % (60 * 60)) + 3600))
  prevHalfHHMM=$(date -d"@$epochPrevHalf" "+%H:%M")
  prevHourHHMM=$(date -d"@$epochPrevHour" "+%H:%M")
  nextHalfHHMM=$(date -d"@$epochNextHalf" "+%H:%M")
  nextHourHHMM=$(date -d"@$epochNextHour" "+%H:%M")
  read curDay curday curweek curMon curmon<<<$(date -d"@$epochPrevHalf" "+%a %d %U b m")
  schedule=$(jq -r '."\($ENV.prevHalfHHMM)"."\($ENV.curDay)"' ${jsonSchedule})
  [ "$schedule" == "null" ] && schedule=$(jq -r '."\($ENV.prevHourHHMM)"."\($ENV.curDay)"' ${jsonSchedule})
  filename=KJZZ_$(date +%Y-%m-%d)_${curDay}_${prevHalfHHMM}-${nextHalfHHMM}_${schedule}.mp3
  echo "                             $HIGH$curHHMM$END" 1>&2
  echo filename=$g$filename$END 1>&2
}

# 5. get all needed values at T time: 1696737782 = Sat 07 Oct 2023 09:03:02 PM MST
epoch=1696737782
# 5.1 filename: KJZZ_2023-10-07_Sat_21:00-21:30_Climate One.mp3
date -d@$epoch
# Sat 07 Oct 2023 02:49:30 PM MST
filename=KJZZ_$(date +%Y-%m-%d)_${prevHalfHHMM}-${nextHalfHHMM}_${schedule}.mp3
echo $filename
# KJZZ_2023-10-07_Sat_21:00-21:30_Climate One.mp3

# 5.2 duration: $secUntilNextHalf
echo $secSinceLastHour $secSinceLastHalf $secUntilNextHalf $secUntilNextHour
# 182 182 1618 3418

# 5. get all needed values at T time: 1696739582 = Sat 07 Oct 2023 09:33:02 PM MST
epoch=1696739582
# 5.1 filename: KJZZ_2023-10-07_Sat_21:00-21:30_Climate One.mp3
date -d@$epoch
# Sat 07 Oct 2023 09:33:02 PM MST
filename=KJZZ_$(date +%Y-%m-%d)_${prevHalfHHMM}-${nextHalfHHMM}_${schedule}.mp3
echo $filename
# KJZZ_2023-10-07_Sat_21:30-22:00_Climate One.mp3

# 5.2 duration: $secUntilNextHalf
echo $secSinceLastHour $secSinceLastHalf $secUntilNextHalf $secUntilNextHour
# 21:03 # 182 182 1618 3418   # KJZZ_2023-10-07_Sat_21:00-21:30_Climate One.mp3
# 21:33 # 1982 182 1618 1618  # KJZZ_2023-10-07_Sat_21:30-22:00_Climate One.mp3
# 21:56 # 3424 1624 176 176   # KJZZ_2023-10-07_Sat_21:30-22:00_Climate One.mp3

curlDownloader() {
  [ -f run.pid ] && echo "run.pid $G$(cat run.pid)$END running, exit." 1>&2 && return 1
  [[ $# == 0 || -z $filename ]] && echo "syntax: curlDownloader : <seconds> [filename] *$g\"$filename\"$END" 1>&2 && return 99
  (($# > 1)) && filename=$2
  
  command="'timeout ${1}s curl \"https://kjzz.streamguys1.com/kjzz_mp3_128\" -H \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0\" -H \"Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5\" -H \"Accept-Language: en-US,en;q=0.5\" -H \"Range: bytes=261876-\" -H \"DNT: 1\" -H \"Connection: keep-alive\" -H \"Sec-Fetch-Dest: audio\" -H \"Sec-Fetch-Mode: no-cors\" -H \"Sec-Fetch-Site: cross-site\" -H \"Accept-Encoding: identity\" >>\"${filename}.mp3\" 2>>kjzzDownloader.out; rm run.pid'"
  echo nohup sh -c ${command} "&" echo $! ">run.pid" 1>&2
  eval nohup sh -c ${command}  &  echo $!  >run.pid
}

kjzzDownloader() {
  scheduler
  [ -f run.pid ] && {
    echo "run.pid $G$(cat run.pid)$END is appending \"${filename}\" for the next $HIGH$((secUntilNextHalf / 60))$END minutes." 1>&2
    return 1
  }
  (($# > 0 )) && echo ok || echo error
  echo curlDownloader $secUntilNextHalf
  date
}

ps -q $(cat run.pid)

if [ -f "${filename}" -a `flock -xn "${filename}" -c 'echo 1'` ]; then 
   echo 'not running'
   echo restart...
else
   ls "${filename}"
   echo -n 'running with PID '
   cat run.pid
fi





























captioning:
-- linux only https://github.com/abb128/LiveCaptions
  git clone https://github.com/abb128/LiveCaptions
  cd LiveCaptions
  git submodule update --init --recursive
-- https://sourceforge.net/projects/javt/
  only WAV
-- https://fosspost.org/open-source-speech-recognition/
--- https://deepspeech.readthedocs.io/en/r0.9/?badge=latest    abandonned
    abandonned for 2 years
--- http://kaldi-asr.org/doc/index.html   could not compile
    abandonned for 1 year
    https://github.com/kaldi-asr/kaldi
    git clone https://github.com/kaldi-asr/kaldi.git kaldi --origin upstream
    cd kaldi
    windows/INSTALL.md
      https://cmake.org/download/
      https://github.com/Kitware/CMake/releases/download/v3.27.6/cmake-3.27.6-windows-x86_64.zip
        set VisualStudio2022=E:\GPT\VisualStudio\2022\BuildTools\VC\Tools\MSVC\14.36.32532\bin\HostX86\x86;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\VC\VCPackages;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\TestWindow;E:\GPT\VisualStudio\2022\BuildTools\MSBuild\Current\bin\Roslyn;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\VC\Linux\bin\ConnectionManagerExe
        set PATH=%PATH%;E:\GPT\KJZZ\cmake-3.27.6-windows-x86_64\bin;%VisualStudio2022%
        git clone https://github.com/kkm000/openfst.git
        cd openfst
        mkdir build64
        cd build64
        del CMakeCache.txt
        vi E:\GPT\KJZZ\openfst\build64\CMakeFiles\3.27.6\VCTargetsPath.vcxproj
        REM cmake -G "Visual Studio 15 2017 Win64" ../
        cmake -G "Visual Studio 17 2022" -A Win64 ../
        
        https://files.portaudio.com/download.html
        git clone https://github.com/PortAudio/portaudio
        cd portaudio
        cmake -G "Visual Studio 17 2022" -A Win64
--- https://github.com/julius-speech/julius             WORKS but SUPER SLOW
    https://github.com/julius-speech/julius/releases
    cd E:\GPT\KJZZ\julius-4.6-win32bin\bin\
    wget https://sourceforge.net/projects/juliusmodels/files/latest/download
    pushd E:\GPT\KJZZ\julius-4.6-win32bin\ENVR-v5.4.Dnn.Bin\

    vi dnn.jconf
    replace
      feature_options -htkconf wav_config -cvn -cmnload ENVR-v5.3.norm -cmnstatic
    by
      feature_options -htkconf wav_config -cvn -cmnload ENVR-v5.3.norm -cvnstatic
    add at the end:
      state_prior_log10nize false

    ..\bin\julius -C julius.jconf -dnnconf dnn.jconf
    
    oracle01:
    cd /docker
    sudo apt -y install build-essential zlib1g-dev libsdl2-dev libasound2-dev mpg123 ffmpeg
    git clone https://github.com/julius-speech/julius.git
    cd julius
      # https://stackoverflow.com/questions/4810996/how-to-resolve-configure-guessing-build-type-failure
    ./configure --build=aarch64-unknown-linux-gnu --enable-words-int
    make -j4
    ls -l julius/julius
    wget "https://downloads.sourceforge.net/project/juliusmodels/ENVR-v5.4.Dnn.Bin.zip?ts=gAAAAABlH0GfXRonhnXpzNNDE4hDZyWkhz4vwhs6mIidXHVZKCZ4Gyf2CoT7e286jC_r_VP1ISnhhKrJzi_C0UDRQ77M7-xIZA%3D%3D&r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fjuliusmodels%2Ffiles%2FENVR-v5.4.Dnn.Bin.zip%2Fdownload" -OENVR-v5.4.Dnn.Bin.zip
    cd /docker/julius/ENVR-v5.4.Dnn.Bin
    
    ../julius/julius -C julius.jconf -dnnconf dnn.jconf -logfile mozilla.out
    # results:
    grep wseq1 mozilla.out
    
    ffmpeg -y -i aaa.mp3 -vn -ar 16000 -ac 1 -b:a 192k aaa.wav && echo aaa.wav >test.dbl
    
    ffprobe aaa.wav -show_format 2>&1
    ffprobe mozilla.wav -show_format 2>&1
      # looks like we need by default: 16000 Hz, 1 channels, s16, 256 kb/s
      
      ../julius/julius -quiet -C julius.jconf -dnnconf dnn.jconf | grep wseq1 | tee -a aaa.out
      -smpFreq 44100
      # results:
      grep wseq1 aaa.out

# pass1_best: <s> isn't about rahman four year </s>
# sentence1: <s> it's about rahman for you </s>
# === begin forced alignment ===
# -- word alignment --
 # id: from  to    n_score    unit
 # ----------------------------------------
# [   0    1]  -6.536312  <s>     [<s>]
# [   2   12]  -0.162462  it's    [it's]
# [  13   49]  1.995572  about    [about]
# [  50   97]  2.767282  rahman   [rahman]
# [  98  120]  2.052484  for      [for]
# [ 121  147]  2.060630  you      [you]
# [ 148  195]  0.199397  </s>     [</s>]
# re-computed AM score: 303.135834
# === end forced alignment ===
# ...

# wseq1: <s> it's about rahman for you </s>
# wseq1: <s> senior pastor has jabbed his soulful </s>
# wseq1: <s> and love </s>
# wseq1: <s> rahm is not fanciful then make it look basiji so they enjoyed a warm bath north like the elections are </s>
# wseq1: <s> when you're down </s>
# wseq1: <s> he's you feel better </s>
# wseq1: <s> he had called hysteria </s>
# wseq1: <s> young panda </s>
# wseq1: <s> and that the fees just salt </s>
# wseq1: <s> so on </s>
# wseq1: <s> you're on </s>
# wseq1: <s> in japan </s>
# wseq1: <s> farmers outside everywhere </s>
# wseq1: <s> the modern examples </s>
# wseq1: <s> and this is perfect because i am not over male colleagues to u.s.c. students </s>
# wseq1: <s> and down </s>
# wseq1: <s> i won't be there for those too </s>


--- https://github.com/flashlight/flashlight        too complex
--- https://github.com/PaddlePaddle/PaddleSpeech    chinese
--- https://github.com/NVIDIA/OpenSeq2Seq           translation not transcription
--- https://alphacephei.com/vosk/
pip3 install vosk

# first run will download vosk-model-small-en-us-0.15.zip:
vosk-transcriber --model-name vosk-model-small-en-us-0.15 -i aaa.mp3 -o aaa-small.txt
vosk-transcriber --model-name vosk-model-small-en-us-0.15 -i test.mp4 -t srt -o test.srt
vosk-transcriber --model-name vosk-model-small-en-us-0.15 -i test.m4a -t srt -o test.srt
vosk-transcriber --list-languages

vosk-transcriber -l en-us -i aaa.mp3 -o aaa-en-us.txt
# what is it about ramen for you seen that so
# most japanese is food
# and
# romney's enough to fancy food then make it look fancy here so they can charge you know more about you know i like to i like
# when you're down
# you eat you feel better
# you have a goal is very good yeah and
# in that our future soul
# so you know in japan
# amish up everywhere
# a more them make dolls <- mcdonald's
# and this is perfect because i have a lot of
# you know college years used to that's
# and
# i want to hear that all those can't

# models:   https://alphacephei.com/vosk/models   https://github.com/daanzu/kaldi-active-grammar/blob/master/docs/models.md
vosk-transcriber --tasks 6 --model-name vosk-model-en-us-0.22-lgraph     -i aaa.mp3 -o aaa-lgraph.txt
# what is it about ramen for you see that that's the most of the japanese his soulful and ramis not the fancy food they make it look fancy here so they can charge you more but you know i like to i like when you're down you eat you feel better
# you have a call is very good you know and
# that that feed your soul
# so you know in japan
# amish ups everywhere
# the more than mcdonald's and this is perfect because i have a lot of you know college us your students and i want to see that all those kids

vosk-transcriber --tasks 6 --model-name vosk-model-en-us-0.22            -i aaa.mp3 -o aaa-0.22.txt

vosk-transcriber --tasks 6 --model-name vosk-model-en-us-0.42-gigaspeech -i aaa.mp3 -o aaa-gigaspeech.txt
# what is it about ramen for you seeing that that's mostly japanese soulful
# and rom is not the fancy food they make it look fancy here so they can charge you no more but you know i like to i like ah
# when you are down you eat you feel better
# you have a coal is very good you know and
# that feature soul
# so you know in japan ami shops everywhere it's more than mcdonnell's and this is perfect because i have a lot of ah you know college usu students and i want to see that all those kids

# https://github.com/benob/recasepunc
wget https://alphacephei.com/vosk/models/vosk-recasepunc-en-0.22.zip
unzip vosk-recasepunc-en-0.22.zip
vosk-transcriber --tasks 6 --model vosk-recasepunc-en-0.22          -i aaa.mp3 -o aaa-recasepunc.txt


vosk-transcriber --help
usage: vosk-transcriber.exe [-h] [--model MODEL] [--server] [--list-models] [--list-languages]
                            [--model-name MODEL_NAME] [--lang LANG] [--input INPUT] [--output OUTPUT]
                            [--output-type OUTPUT_TYPE] [--tasks TASKS] [--log-level LOG_LEVEL]

Transcribe audio file and save result in selected format

options:
  -h, --help            show this help message and exit
  --model MODEL, -m MODEL
                        model path
  --server, -s          use server for recognition
  --list-models         list available models
  --list-languages      list available languages
  --model-name MODEL_NAME, -n MODEL_NAME
                        select model by name
  --lang LANG, -l LANG  select model by language
  --input INPUT, -i INPUT
                        audiofile
  --output OUTPUT, -o OUTPUT
                        optional output filename path
  --output-type OUTPUT_TYPE, -t OUTPUT_TYPE
                        optional arg output data type
  --tasks TASKS, -ts TASKS
                        number of parallel recognition tasks
  --log-level LOG_LEVEL
                        logging level
                        
                        

--- https://github.com/athena-team/athena
    # models: https://github.com/LianjiaTech/athena-model-zoo
    git clone https://github.com/athena-team/athena
    cd athena
    pip install tensorflow-gpu==2.8.0
    pip install -r requirements.txt
    python setup.tf2.8.py bdist_wheel sdist
    python -m pip install --ignore-installed dist/athena-2.0*.whl
    # One wav test
    python athena/run_demo.py --inference_type asr --saved_model_dir examples/asr/aishell/models/freeze_prefix_beam-20220620 --wav_dir aishell/wav/test/S0764/BAC009S0764W0121.wav


--------------- live stream to text: https://singerlinks.com/2022/03/how-to-convert-microphone-speech-to-text-using-python-and-vosk/
pip install sounddevice

import sounddevice as sd
print(sd.query_devices())
  # 0 Microsoft Sound Mapper - Output, MME (0 in, 2 out)
# < 1 Remote Audio, MME (0 in, 2 out)
  # 2 Primary Sound Driver, Windows DirectSound (0 in, 2 out)
  # 3 Remote Audio, Windows DirectSound (0 in, 2 out)
  # 4 Remote Audio, Windows WASAPI (0 in, 2 out)
  # 5 SPDIF Out (HD Audio SPDIF out), Windows WDM-KS (0 in, 2 out)
  # 6 Speakers (HD Audio Speaker), Windows WDM-KS (0 in, 2 out)
  # 7 MIDI (DroidCam Audio), Windows WDM-KS (1 in, 0 out)
  # 8 Output (DroidCam Audio), Windows WDM-KS (0 in, 1 out)
  
--------------- live stream to text: https://singerlinks.com/2022/03/how-to-convert-microphone-speech-to-text-using-python-and-vosk/



--- https://github.com/openai/whisper
# abandonned - i can't get this to work with cuda
# conda update -y -n base -c defaults conda -y
# python -m pip install --upgrade pip
# conda create -y -n kjzz
# conda activate kjzz
# conda install python=3.11 -c conda-forge -y
# conda install cudatoolkit=11.7 -c conda-forge -y

# CPU only:
# pip install -U openai-whisper
# pip install --force-reinstall git+https://github.com/openai/whisper.git 
# pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git

# GPU: https://github.com/openai/whisper/discussions/1463   abandonned - i can't get this to work with cuda
# md E:\GPT\whisper
# cd E:\GPT\whisper
# pip install --force-reinstall git+https://github.com/openai/whisper.git
# pip install blobfile
# wget https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe
# wget https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/encoder.json
# vi E:\GPT\miniconda3\envs\kjzz\Lib\site-packages\tiktoken_ext\openai_public.py
        # vocab_bpe_file="E:/GPT/whisper/vocab.bpe",
        # encoder_json_file="E:/GPT/whisper/encoder.json",

# git clone https://github.com/openai/whisper   abandonned - i can't get this to work with cuda
# cd whisper
# pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu117

# portable: https://github.com/Purfview/whisper-standalone-win
wget https://github.com/Purfview/whisper-standalone-win/releases/download/faster-whisper/Whisper-Faster_r153.zip
unzip Whisper-Faster_r153.zip
set path=E:\GPT\Whisper-Faster\;E:\GPT\miniconda3\envs\h2ogpt\Lib\site-packages\torch\lib\;%PATH%
E:\GPT\Whisper-Faster\whisper-faster.exe

cd E:\GPT\KJZZ
busybox time whisper-faster aaa.mp3 --language en --model small --output_format all --device cuda --output_dir E:\GPT\KJZZ\

small.en gives worst results then small

whisper-faster aaa.mp3 --model small.en                     --device cuda
whisper-faster aaa.mp3 --model small.en --output_format txt --device cuda
whisper-faster aaa.mp3 --model small.en --output_format txt --device cuda
# What is it about ramen for you?
# See, that's Japanese soul food.
# And ramen is not the fancy food.
# They make it look fancy here so they can charge it more.
# But I like when you are down, you feel better.
# You have a cold.
# It's very good.
# And that feeds your soul.
# So in Japan, ramen shops are everywhere.
# It's more than McDonald's.
# And this is perfect because I have a lot of college USU
# students.
# And I want to feed all those kids.

whisper-faster aaa.mp3 --model tiny --output_format txt --device cuda
# What is it about ramen for you?
# See, that's a nice Japanese soft food.
# And ramen is not the fancy food.
# They make it look fancy here, so they can charge more.
# But you know, I like to, I like when you are down,
# you feel better.
# You have a cold, it's very good, you know,
# and that's a feature of a soul.
# So, you know, in Japan, I make shops everywhere.
# It's a more than McDonald's.
# And this is perfect because I have a lot of college,
# as you students, and I won't feel that all those kids.

whisper-faster aaa.mp3 --model base --output_format txt --device cuda
# What is it about ramen for you?
# See, that's the Japanese soul food.
# And ramen is not the fancy food.
# They make it look fancy here, so they can charge it more.
# But I like when you are down, you feel better.
# You have a cold.
# It's very good.
# And that feature is all.
# So, you know, in Japan, ramen shops are everywhere.
# The more they make dolls.
# And this is perfect because I have a lot of college students.
# And I want to feed all those kids.


# whisper aaa.mp3 --model small --output_format txt --device cuda
# RuntimeError: Attempting to deserialize object on a CUDA device but torch.cuda.is_available() is False. If you are running on a CPU-only machine, please use torch.load with map_location=torch.device('cpu') to map your storages to the CPU.


whisper-faster aaa.mp3 --task translate

whisper-faster --help
# usage: whisper [-h] [--model {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large-v1,large-v2,large}]
               # [--model_dir MODEL_DIR] [--device DEVICE] [--output_dir OUTPUT_DIR]
               # [--output_format {txt,vtt,srt,tsv,json,all}] [--verbose VERBOSE] [--task {transcribe,translate}]
               # [--language {af,am,ar,as,az,ba,be,bg,bn,bo,br,bs,ca,cs,cy,da,de,el,en,es,et,eu,fa,fi,fo,fr,gl,gu,ha,haw,he,hi,hr,ht,hu,hy,id,is,it,ja,jw,ka,kk,km,kn,ko,la,lb,ln,lo,lt,lv,mg,mi,mk,ml,mn,mr,ms,mt,my,ne,nl,nn,no,oc,pa,pl,ps,pt,ro,ru,sa,sd,si,sk,sl,sn,so,sq,sr,su,sv,sw,ta,te,tg,th,tk,tl,tr,tt,uk,ur,uz,vi,yi,yo,zh,Afrikaans,Albanian,Amharic,Arabic,Armenian,Assamese,Azerbaijani,Bashkir,Basque,Belarusian,Bengali,Bosnian,Breton,Bulgarian,Burmese,Castilian,Catalan,Chinese,Croatian,Czech,Danish,Dutch,English,Estonian,Faroese,Finnish,Flemish,French,Galician,Georgian,German,Greek,Gujarati,Haitian,Haitian Creole,Hausa,Hawaiian,Hebrew,Hindi,Hungarian,Icelandic,Indonesian,Italian,Japanese,Javanese,Kannada,Kazakh,Khmer,Korean,Lao,Latin,Latvian,Letzeburgesch,Lingala,Lithuanian,Luxembourgish,Macedonian,Malagasy,Malay,Malayalam,Maltese,Maori,Marathi,Moldavian,Moldovan,Mongolian,Myanmar,Nepali,Norwegian,Nynorsk,Occitan,Panjabi,Pashto,Persian,Polish,Portuguese,Punjabi,Pushto,Romanian,Russian,Sanskrit,Serbian,Shona,Sindhi,Sinhala,Sinhalese,Slovak,Slovenian,Somali,Spanish,Sundanese,Swahili,Swedish,Tagalog,Tajik,Tamil,Tatar,Telugu,Thai,Tibetan,Turkish,Turkmen,Ukrainian,Urdu,Uzbek,Valencian,Vietnamese,Welsh,Yiddish,Yoruba}]
               # [--temperature TEMPERATURE] [--best_of BEST_OF] [--beam_size BEAM_SIZE] [--patience PATIENCE]
               # [--length_penalty LENGTH_PENALTY] [--suppress_tokens SUPPRESS_TOKENS] [--initial_prompt INITIAL_PROMPT]
               # [--condition_on_previous_text CONDITION_ON_PREVIOUS_TEXT] [--fp16 FP16]
               # [--temperature_increment_on_fallback TEMPERATURE_INCREMENT_ON_FALLBACK]
               # [--compression_ratio_threshold COMPRESSION_RATIO_THRESHOLD] [--logprob_threshold LOGPROB_THRESHOLD]
               # [--no_speech_threshold NO_SPEECH_THRESHOLD] [--word_timestamps WORD_TIMESTAMPS]
               # [--prepend_punctuations PREPEND_PUNCTUATIONS] [--append_punctuations APPEND_PUNCTUATIONS]
               # [--highlight_words HIGHLIGHT_WORDS] [--max_line_width MAX_LINE_WIDTH] [--max_line_count MAX_LINE_COUNT]
               # [--threads THREADS]
               # audio [audio ...]

# positional arguments:
  # audio                 audio file(s) to transcribe

# options:
  # -h, --help            show this help message and exit
  # --model {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large-v1,large-v2,large}
                        # name of the Whisper model to use (default: small)
  # --model_dir MODEL_DIR
                        # the path to save model files; uses ~/.cache/whisper by default (default: None)
  # --device DEVICE       device to use for PyTorch inference (default: cpu)
  # --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        # directory to save the outputs (default: .)
  # --output_format {txt,vtt,srt,tsv,json,all}, -f {txt,vtt,srt,tsv,json,all}
                        # format of the output file; if not specified, all available formats will be produced (default:
                        # all)
  # --verbose VERBOSE     whether to print out the progress and debug messages (default: True)
  # --task {transcribe,translate}
                        # whether to perform X->X speech recognition ('transcribe') or X->English translation
                        # ('translate') (default: transcribe)
  # --language {af,am,ar,as,az,ba,be,bg,bn,bo,br,bs,ca,cs,cy,da,de,el,en,es,et,eu,fa,fi,fo,fr,gl,gu,ha,haw,he,hi,hr,ht,hu,hy,id,is,it,ja,jw,ka,kk,km,kn,ko,la,lb,ln,lo,lt,lv,mg,mi,mk,ml,mn,mr,ms,mt,my,ne,nl,nn,no,oc,pa,pl,ps,pt,ro,ru,sa,sd,si,sk,sl,sn,so,sq,sr,su,sv,sw,ta,te,tg,th,tk,tl,tr,tt,uk,ur,uz,vi,yi,yo,zh,Afrikaans,Albanian,Amharic,Arabic,Armenian,Assamese,Azerbaijani,Bashkir,Basque,Belarusian,Bengali,Bosnian,Breton,Bulgarian,Burmese,Castilian,Catalan,Chinese,Croatian,Czech,Danish,Dutch,English,Estonian,Faroese,Finnish,Flemish,French,Galician,Georgian,German,Greek,Gujarati,Haitian,Haitian Creole,Hausa,Hawaiian,Hebrew,Hindi,Hungarian,Icelandic,Indonesian,Italian,Japanese,Javanese,Kannada,Kazakh,Khmer,Korean,Lao,Latin,Latvian,Letzeburgesch,Lingala,Lithuanian,Luxembourgish,Macedonian,Malagasy,Malay,Malayalam,Maltese,Maori,Marathi,Moldavian,Moldovan,Mongolian,Myanmar,Nepali,Norwegian,Nynorsk,Occitan,Panjabi,Pashto,Persian,Polish,Portuguese,Punjabi,Pushto,Romanian,Russian,Sanskrit,Serbian,Shona,Sindhi,Sinhala,Sinhalese,Slovak,Slovenian,Somali,Spanish,Sundanese,Swahili,Swedish,Tagalog,Tajik,Tamil,Tatar,Telugu,Thai,Tibetan,Turkish,Turkmen,Ukrainian,Urdu,Uzbek,Valencian,Vietnamese,Welsh,Yiddish,Yoruba}
                        # language spoken in the audio, specify None to perform language detection (default: None)
  # --temperature TEMPERATURE
                        # temperature to use for sampling (default: 0)
  # --best_of BEST_OF     number of candidates when sampling with non-zero temperature (default: 5)
  #    BEAM_SIZE
                        # number of beams in beam search, only applicable when temperature is zero (default: 5)
  # --patience PATIENCE   optional patience value to use in beam decoding, as in https://arxiv.org/abs/2204.05424, the
                        # default (1.0) is equivalent to conventional beam search (default: None)
  # --length_penalty LENGTH_PENALTY
                        # optional token length penalty coefficient (alpha) as in https://arxiv.org/abs/1609.08144, uses
                        # simple length normalization by default (default: None)
  # --suppress_tokens SUPPRESS_TOKENS
                        # comma-separated list of token ids to suppress during sampling; '-1' will suppress most special
                        # characters except common punctuations (default: -1)
  # --initial_prompt INITIAL_PROMPT
                        # optional text to provide as a prompt for the first window. (default: None)
  # --condition_on_previous_text CONDITION_ON_PREVIOUS_TEXT
                        # if True, provide the previous output of the model as a prompt for the next window; disabling
                        # may make the text inconsistent across windows, but the model becomes less prone to getting
                        # stuck in a failure loop (default: True)
  # --fp16 FP16           whether to perform inference in fp16; True by default (default: True)
  # --temperature_increment_on_fallback TEMPERATURE_INCREMENT_ON_FALLBACK
                        # temperature to increase when falling back when the decoding fails to meet either of the
                        # thresholds below (default: 0.2)
  # --compression_ratio_threshold COMPRESSION_RATIO_THRESHOLD
                        # if the gzip compression ratio is higher than this value, treat the decoding as failed
                        # (default: 2.4)
  # --logprob_threshold LOGPROB_THRESHOLD
                        # if the average log probability is lower than this value, treat the decoding as failed
                        # (default: -1.0)
  # --no_speech_threshold NO_SPEECH_THRESHOLD
                        # if the probability of the <|nospeech|> token is higher than this value AND the decoding has
                        # failed due to `logprob_threshold`, consider the segment as silence (default: 0.6)
  # --word_timestamps WORD_TIMESTAMPS
                        # (experimental) extract word-level timestamps and refine the results based on them (default:
                        # False)
  # --prepend_punctuations PREPEND_PUNCTUATIONS
                        # if word_timestamps is True, merge these punctuation symbols with the next word (default:
                        # "'“¿([{-)
  # --append_punctuations APPEND_PUNCTUATIONS
                        # if word_timestamps is True, merge these punctuation symbols with the previous word (default:
                        # "'.。,，!！?？:：”)]}、)
  # --highlight_words HIGHLIGHT_WORDS
                        # (requires --word_timestamps True) underline each word as it is spoken in srt and vtt (default:
                        # False)
  # --max_line_width MAX_LINE_WIDTH
                        # (requires --word_timestamps True) the maximum number of characters in a line before breaking
                        # the line (default: None)
  # --max_line_count MAX_LINE_COUNT
                        # (requires --word_timestamps True) the maximum number of lines in a segment (default: None)
  # --threads THREADS     number of threads used by torch for CPU inference; supercedes MKL_NUM_THREADS/OMP_NUM_THREADS
                        # (default: 0)


-- https://github.com/ggerganov/whisper.cpp
wget https://github.com/ggerganov/whisper.cpp/releases/download/v1.4.0/whisper-blas-bin-x64.zip

cd E:\GPT\whisper-bin-x64\
:: https://github.com/ggerganov/whisper.cpp/tree/master/models
md models
cd models
wget https://raw.githubusercontent.com/ggerganov/whisper.cpp/master/models/download-ggml-model.cmd
download-ggml-model.cmd small.en

ffmpeg -y -i "E:\GPT\KJZZ\41\KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.mp3" -vn -ar 16000 -ac 1 -b:a 192k "E:\GPT\KJZZ\41\KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.wav"
set WHISPER_CUBLAS=1
main.exe --print-progress --output-file E:\GPT\KJZZ\41\ -m models/ggml-small.en.bin "E:\GPT\KJZZ\41\KJZZ_2023-10-08_Sun_2300-2330_BBC World Service.wav"

--> not using cuda... moving on.

main.exe
# error: no input files specified

# usage: main.exe [options] file0.wav file1.wav ...

# options:
  # -h,        --help              [default] show this help message and exit
  # -t N,      --threads N         [4      ] number of threads to use during computation
  # -p N,      --processors N      [1      ] number of processors to use during computation
  # -ot N,     --offset-t N        [0      ] time offset in milliseconds
  # -on N,     --offset-n N        [0      ] segment index offset
  # -d  N,     --duration N        [0      ] duration of audio to process in milliseconds
  # -mc N,     --max-context N     [-1     ] maximum number of text context tokens to store
  # -ml N,     --max-len N         [0      ] maximum segment length in characters
  # -sow,      --split-on-word     [false  ] split on word rather than on token
  # -bo N,     --best-of N         [2      ] number of best candidates to keep
  # -bs N,     --beam-size N       [-1     ] beam size for beam search
  # -wt N,     --word-thold N      [0.01   ] word timestamp probability threshold
  # -et N,     --entropy-thold N   [2.40   ] entropy threshold for decoder fail
  # -lpt N,    --logprob-thold N   [-1.00  ] log probability threshold for decoder fail
  # -su,       --speed-up          [false  ] speed up audio by x2 (reduced accuracy)
  # -tr,       --translate         [false  ] translate from source language to english
  # -di,       --diarize           [false  ] stereo audio diarization
  # -nf,       --no-fallback       [false  ] do not use temperature fallback while decoding
  # -otxt,     --output-txt        [false  ] output result in a text file
  # -ovtt,     --output-vtt        [false  ] output result in a vtt file
  # -osrt,     --output-srt        [false  ] output result in a srt file
  # -olrc,     --output-lrc        [false  ] output result in a lrc file
  # -owts,     --output-words      [false  ] output script for generating karaoke video
  # -fp,       --font-path         [/System/Library/Fonts/Supplemental/Courier New Bold.ttf] path to a monospace font for karaoke video
  # -ocsv,     --output-csv        [false  ] output result in a CSV file
  # -oj,       --output-json       [false  ] output result in a JSON file
  # -of FNAME, --output-file FNAME [       ] output file path (without file extension)
  # -ps,       --print-special     [false  ] print special tokens
  # -pc,       --print-colors      [false  ] print colors
  # -pp,       --print-progress    [false  ] print progress
  # -nt,       --no-timestamps     [true   ] do not print timestamps
  # -l LANG,   --language LANG     [en     ] spoken language ('auto' for auto-detect)
             # --prompt PROMPT     [       ] initial prompt
  # -m FNAME,  --model FNAME       [models/ggml-base.en.bin] model path
  # -f FNAME,  --file FNAME        [       ] input WAV file path

