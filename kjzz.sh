#!/usr/bin/env bash
TZ=America/Phoenix

scheduler() {
  # date
  local allexport=true; set -a

  epoch=$(date +%s)
  (($# > 0)) && jsonSchedule=$1
  (($# > 1)) && epoch=$2
  curHHMM=$(date -d"@$epoch" "+%H:%M")
  secSinceLastHour=$(( $epoch % 3600 ))
  secSinceLastHalf=$(( $epoch % 1800 ))
  # # add +1s to make sure we do not restart 1s before
  # secUntilNextHour=$(( 1 + 3600 - $epoch % 3600 ))
  # secUntilNextHalf=$(( 1 + 1800 - $epoch % 1800 ))
  # no, let's try and let cron handle it, minus 1s
  secUntilNextHour=$(( 3600 - 1 - $epoch % 3600 ))
  secUntilNextHalf=$(( 1800 - 1 - $epoch % 1800 ))
  epochPrevHalf=$(($epoch - ($epoch % (30 * 60))))
  epochPrevHour=$(($epoch - ($epoch % (60 * 60))))
  epochNextHalf=$(($epoch - ($epoch % (30 * 60)) + 1800))
  epochNextHour=$(($epoch - ($epoch % (60 * 60)) + 3600))
  prevHalfHH_MM=$(date -d"@$epochPrevHalf" "+%H:%M")
  prevHourHH_MM=$(date -d"@$epochPrevHour" "+%H:%M")
  nextHalfHH_MM=$(date -d"@$epochNextHalf" "+%H:%M")
  nextHourHH_MM=$(date -d"@$epochNextHour" "+%H:%M")
  prevHalfHHMM=$(date -d"@$epochPrevHalf" "+%H%M")
  prevHourHHMM=$(date -d"@$epochPrevHour" "+%H%M")
  nextHalfHHMM=$(date -d"@$epochNextHalf" "+%H%M")
  nextHourHHMM=$(date -d"@$epochNextHour" "+%H%M")
  read curDay curday isoweek curMon curmon<<<$(date -d"@$epochPrevHalf" "+%a %d %V b m")
  schedule=$(jq -r '."\($ENV.prevHalfHH_MM)"."\($ENV.curDay)"' ${jsonSchedule})
  [ "$schedule" == "null" ] && schedule=$(jq -r '."\($ENV.prevHourHH_MM)"."\($ENV.curDay)"' ${jsonSchedule})
  
  filename=KJZZ_$(date +%Y-%m-%d)_${curDay}_${prevHalfHHMM}-${nextHalfHHMM}_${schedule}.mp3
  [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && _color=$r || _color=$g
  echo "                             $HIGH$curHHMM$END" | tee -a $LOG 1>&2
  echo filename=$_color$filename$END | tee -a $LOG 1>&2
}

curlDownloader() {
  [ -f "${PIDFILE}" ] && echo "kjzzDownloader $G$(cat ${PIDFILE})$END already running." | tee -a $LOG 1>&2 && return 1
  [[ $# == 0 ]] && echo "syntax: curlDownloader : <seconds> [filename] *$g\"$filename\"$END" | tee -a $LOG 1>&2 && return 99
  (($# > 0)) && seconds=$1
  (($# > 1)) && filename=$2
  [ ! -f "$FLAG" ] && echo "${FLAG} missing. touch ${FLAG}" | tee -a $LOG 1>&2 && return 1
  
  # command="'timeout ${seconds}s curl \"https://kjzz.streamguys1.com/kjzz_mp3_128\" -H \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0\" -H \"Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5\" -H \"Accept-Language: en-US,en;q=0.5\" -H \"Range: bytes=261876-\" -H \"DNT: 1\" -H \"Connection: keep-alive\" -H \"Sec-Fetch-Dest: audio\" -H \"Sec-Fetch-Mode: no-cors\" -H \"Sec-Fetch-Site: cross-site\" -H \"Accept-Encoding: identity\" >>\"${ROOT}/${isoweek}/${filename}\" 2>>\"${ROOT}/${isoweek}/${filename}.log\"; rm ${PIDFILE}; nohup ${ROOT}/kjzz.sh start &'"
  # [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && command="'sleep ${seconds}; rm ${PIDFILE}; nohup ${ROOT}/kjzz.sh start &'"
  command="'timeout ${seconds}s curl \"https://kjzz.streamguys1.com/kjzz_mp3_128\" -H \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0\" -H \"Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5\" -H \"Accept-Language: en-US,en;q=0.5\" -H \"Range: bytes=261876-\" -H \"DNT: 1\" -H \"Connection: keep-alive\" -H \"Sec-Fetch-Dest: audio\" -H \"Sec-Fetch-Mode: no-cors\" -H \"Sec-Fetch-Site: cross-site\" -H \"Accept-Encoding: identity\" >>\"${ROOT}/${isoweek}/${filename}\" 2>>\"${ROOT}/${isoweek}/${filename}.log\"; rm ${PIDFILE};'"
  [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && command="'sleep ${seconds}; rm ${PIDFILE};'"
  [ ! -d "${ROOT}/${isoweek}" ] && mkdir ${ROOT}/${isoweek}
  
  echo nohup sh -c ${command} "&" echo \$! ">${PIDFILE}" | tee -a $LOG 1>&2
  eval nohup sh -c ${command} >>$LOG 2>&1 &  echo $!  >${PIDFILE}
  echo kjzzDownloader $G$!$END now running. | tee -a $LOG 1>&2
  sudo chown -R 1000:1000 ${ROOT} 2>/dev/null
}

kjzzDownloader() {
  scheduler

  COMMAND=
  RETURN=99
  PID=
  KJZZ_PID=false
  KJZZ_PID_RUNNING=false
  KJZZ_FILE=false
  KJZZ_FILE_LOCK=false
  [ ! -f "$FLAG" ] && echo "${FLAG} missing. touch ${FLAG}" | tee -a $LOG 1>&2 && return 1

  (($# > 0 )) && COMMAND=$1

  [ -f "${ROOT}/${isoweek}/${filename}" ]  && KJZZ_FILE=true && lsof "${ROOT}/${isoweek}/${filename}" >/dev/null 2>&1 && KJZZ_FILE_LOCK=true
  [ -f "${PIDFILE}" ]      && KJZZ_PID=true && PID=$(cat ${PIDFILE})
  [ -n "$PID" ]         && ps -q $PID >/dev/null 2>&1 && KJZZ_PID_RUNNING=true
  
  [ $KJZZ_PID_RUNNING == true -a $KJZZ_FILE_LOCK == true ]  && echo "kjzzDownloader $G$PID$END is appending \"${filename}\" for the next $HIGH$((secUntilNextHalf / 60))$END mm = $secUntilNextHalf s. stop it?" | tee -a $LOG 1>&2 && RETURN=1
  [ $KJZZ_PID_RUNNING == true -a $KJZZ_FILE_LOCK == false ] && {
    [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && {
      echo "Will NOT download music. Sleeping for the next $HIGH$((secUntilNextHalf / 60))$END mn = $secUntilNextHalf s. stop it?" | tee -a $LOG 1>&2 && RETURN=0
    } || {
      echo "ERROR: kjzzDownloader $G$PID$END is running but NOT appending \"${filename}\". stop it?" | tee -a $LOG 1>&2
      RETURN=2
    }
  }
  [ $KJZZ_PID == true -a $KJZZ_PID_RUNNING == false ]       && {
    echo "WARNING: kjzzDownloader $G$PID$END detected but not running. Deleted kjzz.pid" | tee -a $LOG 1>&2
    KJZZ_PID=false
    rm ${PIDFILE}
    RETURN=4
  }
  [ $KJZZ_PID == false -a $KJZZ_FILE_LOCK == true ] && {
    # It is implied that there can be only one downloader per server. 
    # Also we proved that {filename} is locked by a process with lsof. PID cannot be null
    PID=$(pgrep -f "${filename}" | head -1)
    echo "kjzz.pid $G$PID$END was missing, is appending \"${filename}\" for the next $HIGH$((secUntilNextHalf / 60))$END mm = $secUntilNextHalf s. stop it?" | tee -a $LOG 1>&2
    echo $PID >${PIDFILE}
    RETURN=5
  }
  [ $KJZZ_PID == false -a $KJZZ_FILE_LOCK == false ] && {
    [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && echo "Will NOT download music." | tee -a $LOG 1>&2
    echo "NOT RUNNING. start it?" | tee -a $LOG 1>&2
    [ -f "$LOG" ] && rm $LOG
    RETURN=0
  }
  
  [ "$COMMAND" == "stop" -a $KJZZ_PID_RUNNING == true ] && pkill -TERM -P "$PID" && rm ${PIDFILE} && echo "kjzz.pid $G$PID$END killed." | tee -a $LOG 1>&2 && RETURN=0
  [ "$COMMAND" == "start" -a -f "$FLAG" ] && curlDownloader $secUntilNextHalf && RETURN=0
  
  return $RETURN
}

export ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PIDFILE=${ROOT}/kjzz.pid
export LOG=${ROOT}/kjzz.out
export FLAG=${ROOT}/kjzz.start
export jsonSchedule=${ROOT}/KJZZ-schedule.json

kjzzDownloader $*

# timeout 1h curl "https://kjzz.streamguys1.com/kjzz_mp3_128" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0" -H "Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5" -H "Accept-Language: en-US,en;q=0.5" -H "Range: bytes=261876-" -H "DNT: 1" -H "Connection: keep-alive" -H "Sec-Fetch-Dest: audio" -H "Sec-Fetch-Mode: no-cors" -H "Sec-Fetch-Site: cross-site" -H "Accept-Encoding: identity" >bbb.mp3
# vi /etc/cron.d/kjzzDownloader
# SHELL=/usr/bin/bash
# PATH=/exploit/bin:/exploit/PATH/was:/exploit/PATH/profile:/exploit/PATH/PLI:/exploit/PATH/Linux:/exploit/PATH/common:/exploit/PATH/aws:/exploit/PATH/apache:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/sbin:/usr/local/bin:/snap/bin
# 0,1,30,31 * * * *   root /docker/kjzz/kjzz.sh start

