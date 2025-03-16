#!/usr/bin/env bash
# This is an automated mp3 stream downloaded based off a json schedule you need to build.
# This program shall be scheduled every second in cron, therefore make sure it runs under 1s
TZ=America/Phoenix

scheduler() {
  # takes 1 optional paramter: jsonSchedule (for testing)
  local allexport=true; set -a

  epoch=$(date +%s)
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
  epochPrevHalf2=$(($epoch - ($epoch % (60 * 60))))
  epochPrevHour2=$(($epoch - ($epoch % (90 * 60))))
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
  
  # https://unix.stackexchange.com/questions/282609/how-to-use-the-date-command-to-display-week-number-of-the-year
  # here we build the values for the current chunk to download, that started within the last 59 minutes
  # calendar ISO:    %V = week 01-01  ISO week number, with Monday as first day of week (01..53)      << LIARS!! 2023-01-01-Sun is week 52 year 2022
  # calendar normal: %W = week 00-53  week number of year, with Monday as first day of week (00..53)  << the one we chose
  # calendar normal: %U = week 00-53  week number of year, with Sunday as first day of week (00..53)
  # date -d "20230101" +"%F-%a is week %V year %G"   # 2023-01-01-Sun is week 52 year 2022   <<-!!
  # date -d "20231231" +"%F-%a is week %V year %G"   # 2023-01-01-Sun is week 52 year 2023
  # date -d "20240101" +"%F-%a is week %V year %G"   # 2024-01-01-Mon is week 01 year 2024
  # date -d "20241231" +"%F-%a is week %V year %G"   # 2024-12-31-Tue is week 01 year 2025   <<-!!
  
  # %W is the best choice as it does not loop, starts Mon, and uses %Y
  # drawback: Now we must decrement some folders in 2025
  # drawback: Can we get same values from strftime('%W','2025-01-01')? YES we tested 2023/4/5 and weekNumber values match %W
  # date -d "20230101" +"%F-%a is week %W year %Y"   # 2023-01-01-Sun is week 00 year 2023
  # date -d "20231231" +"%F-%a is week %W year %Y"   # 2023-01-01-Sun is week 52 year 2023
  # date -d "20240101" +"%F-%a is week %W year %Y"   # 2024-01-01-Mon is week 01 year 2024
  # date -d "20241231" +"%F-%a is week %W year %Y"   # 2024-12-31-Tue is week 53 year 2024
  
  # date -d "20230101" +"%F-%a is week %V/%G %W %U year %Y"   # 2023-01-01-Sun is week 52/2022 00 01 year 2023  no order change needed
  # date -d "20231106" +"%F-%a is week %V/%G %W %U year %Y"   # 2023-11-06-Mon is week 45/2023 45 45 year 2023
  # date -d "20231231" +"%F-%a is week %V/%G %W %U year %Y"   # 2023-12-31-Sun is week 52/2023 52 53 year 2023
  # date -d "20240101" +"%F-%a is week %V/%G %W %U year %Y"   # 2024-01-01-Mon is week 01/2024 01 00 year 2024  no order change needed
  # date -d "20240826" +"%F-%a is week %V/%G %W %U year %Y"   # 2024-08-26-Mon is week 35/2024 35 34 year 2024
  # date -d "20241231" +"%F-%a is week %V/%G %W %U year %Y"   # 2024-12-31-Tue is week 01/2025 53 52 year 2024
  # date -d "20250101" +"%F-%a is week %V/%G %W %U year %Y"   # 2025-01-01-Wed is week 01/2025 00 00 year 2025  -1 for each folder
  # date -d "20250224" +"%F-%a is week %V/%G %W %U year %Y"   # 2025-02-24-Mon is week 09/2025 08 08 year 2025
  # date -d "20251231" +"%F-%a is week %V/%G %W %U year %Y"   # 2025-12-31-Wed is week 01/2026 52 52 year 2025
      # Fri     07      10    Mar     03    2025
  # read curDay curday isoweek curMon curmon curyear<<<$(date -d"@$epochPrevHalf" "+%a %d %V %b %m %Y")
  read curDay curday isoweek curMon curmon curyear<<<$(date -d"@$epochPrevHalf" "+%a %d %W %b %m %Y")
  
  # export jsonSchedule=$(command ls -v ${ROOT}/*json | tail -1)
  # check for the latest updated schedule in order: KJZZ-schedule.json, KJZZ-schedule-20240101.json, KJZZ-schedule-20240415.json
  export jsonSchedule=${ROOT}/KJZZ-schedule.json
  while read schedule; do
    scheduleStart=$(echo ${schedule##*-} | cut -c1-8)
    scheduleWeek=$(date -d "${scheduleStart}" +"%W")
    # this way we can create schedules ahead of time
    [ "${scheduleWeek}" -le "${isoweek}" ] && export jsonSchedule=${schedule}
  done <<<$(ls -v ${ROOT}/KJZZ-schedule-${curyear}????.json 2>/dev/null)
  
  (($# > 0)) && jsonSchedule=$1
  
  programFound=true
  program=$(jq -r '."\($ENV.prevHalfHH_MM)"."\($ENV.curDay)"' ${jsonSchedule})
  [ "$program" == "null" ] && program=$(jq -r '."\($ENV.prevHourHH_MM)"."\($ENV.curDay)"' ${jsonSchedule}) && currentStart=$prevHalfHH_MM || currentStart=$prevHourHH_MM
  [ "$program" == "null" ] && programFound=false && echo "${Y}program:  WARNING: program name not detected - check ${jsonSchedule}${END}"
  
  # KJZZ_2025-03-08_Sat_1630-1700_All Things Considered.mp3
  filename=KJZZ_$(date +%Y-%m-%d)_${curDay}_${prevHalfHHMM}-${nextHalfHHMM}_${program}.mp3
  
  if [ "$COMMAND" == "--help" ]; then
    # imperfect close to 12AM but who cares:
    prevHalfHH_MM2=$(date -d"@$epochPrevHalf2" "+%H:%M")
    prevHourHH_MM2=$(date -d"@$epochPrevHour2" "+%H:%M")
    programPrev="$(jq -r '."\($ENV.prevHalfHH_MM2)"."\($ENV.curDay)"' ${jsonSchedule})" && prevStart=$prevHalfHH_MM2
    [ "$programPrev" == "null" -o "$programPrev" == "$program" ] && programPrev="$(jq -r '."\($ENV.prevHourHH_MM2)"."\($ENV.curDay)"' ${jsonSchedule})" && prevStart=$prevHourHH_MM2
    programNext="$(jq -r '."\($ENV.nextHalfHH_MM)"."\($ENV.curDay)"' ${jsonSchedule})" && nextStart=$nextHalfHH_MM
    [ "$programNext" == "null" ] && programNext="$(jq -r '."\($ENV.nextHourHH_MM)"."\($ENV.curDay)"' ${jsonSchedule})" && nextStart=$nextHourHH_MM
  fi
  
  # exclude musical programs
  [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && _color=$r || _color=$g
  echo "                             $HIGH$curHHMM$END" 1>&2
  echo "filename=$_color$filename$END" 1>&2
}

curlDownloader() {
  [ -f "${PIDFILE}" ] && echo "$curyear-$curmon-$curday $curHHMM kjzzDownloader $G$(cat ${PIDFILE})$END already running." | tee -a $LOG 1>&2 && return 1
  [[ $# == 0 ]] && echo "syntax: curlDownloader : <seconds> [filename] *$g\"$filename\"$END" | tee -a $LOG 1>&2 && return 99
  (($# > 0)) && seconds=$1
  (($# > 1)) && filename=$2
  [ ! -f "$FLAG" ] && echo "${FLAG} missing. touch ${FLAG}" | tee -a $LOG 1>&2 && return 1
  
  # command="'timeout ${seconds}s curl \"https://kjzz.streamguys1.com/kjzz_mp3_128\" -H \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0\" -H \"Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5\" -H \"Accept-Language: en-US,en;q=0.5\" -H \"Range: bytes=261876-\" -H \"DNT: 1\" -H \"Connection: keep-alive\" -H \"Sec-Fetch-Dest: audio\" -H \"Sec-Fetch-Mode: no-cors\" -H \"Sec-Fetch-Site: cross-site\" -H \"Accept-Encoding: identity\" >>\"${ROOT}/${curyear}/${isoweek}/${filename}\" 2>>\"${ROOT}/${curyear}/${isoweek}/${filename}.log\"; rm ${PIDFILE}; nohup ${ROOT}/kjzz.sh start &'"
  # [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && command="'sleep ${seconds}; rm ${PIDFILE}; nohup ${ROOT}/kjzz.sh start &'"
  command="'timeout ${seconds}s curl \"https://kjzz.streamguys1.com/kjzz_mp3_128\" -H \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0\" -H \"Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5\" -H \"Accept-Language: en-US,en;q=0.5\" -H \"Range: bytes=261876-\" -H \"DNT: 1\" -H \"Connection: keep-alive\" -H \"Sec-Fetch-Dest: audio\" -H \"Sec-Fetch-Mode: no-cors\" -H \"Sec-Fetch-Site: cross-site\" -H \"Accept-Encoding: identity\" >>\"${ROOT}/${curyear}/${isoweek}/${filename}\" 2>>\"${ROOT}/${curyear}/${isoweek}/${filename}.log\"; rm ${PIDFILE};'"
  command="'timeout ${seconds}s curl \"https://kjzz.streamguys1.com/kjzz_mp3_128\" -H \"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0\" -H \"Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5\" -H \"Accept-Language: en-US,en;q=0.5\" -H \"Range: bytes=261876-\" -H \"DNT: 1\" -H \"Connection: keep-alive\" -H \"Sec-Fetch-Dest: audio\" -H \"Sec-Fetch-Mode: no-cors\" -H \"Sec-Fetch-Site: cross-site\" -H \"Accept-Encoding: identity\" >>\"${ROOT}/${curyear}/${isoweek}/${filename}\" 2>>/dev/null; rm ${PIDFILE};'"
  [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && command="'sleep ${seconds}; rm ${PIDFILE};'"
  [ ! -d "${ROOT}/${curyear}/${isoweek}" ] && mkdir -p ${ROOT}/${curyear}/${isoweek}
  
  # echo nohup sh -c ${command} "&" echo \$! ">${PIDFILE}" | tee -a $LOG 1>&2
  echo nohup sh -c ${command} "&" echo \$! ">${PIDFILE}" 1>&2
  eval nohup sh -c ${command} &  echo $!  >${PIDFILE}
  echo $curyear-$curmon-$curday $curHHMM kjzzDownloader $G$!$END now running. | tee -a $LOG 1>&2
  sudo chown -R 1000:1000 ${ROOT} 2>/dev/null
}

kjzzDownloader() {
  export COMMAND=
  RETURN=99
  PID=
  KJZZ_PID=false
  KJZZ_PID_RUNNING=false
  KJZZ_FILE=false
  KJZZ_FILE_LOCK=false

  (($# > 0 )) && COMMAND=$1
  [ "$COMMAND" == "disable" ] && rm -f ${FLAG} && echo "rm -f ${FLAG}: download is now disabled." | tee -a $LOG 1>&2 && return 0
  [ "$COMMAND" == "enable" ]  && touch ${FLAG} && echo "touch ${FLAG}: download is now enabled." | tee -a $LOG 1>&2 && return 0

  [ ! -f "$FLAG" ] && echo "$curyear-$curmon-$curday $curHHMM ${FLAG} missing. touch ${FLAG}" | tee -a $LOG 1>&2 && return 1
  scheduler

  [ -f "${ROOT}/${curyear}/${isoweek}/${filename}" ]  && KJZZ_FILE=true && lsof "${ROOT}/${curyear}/${isoweek}/${filename}" >/dev/null 2>&1 && KJZZ_FILE_LOCK=true
  [ -f "${PIDFILE}" ]      && KJZZ_PID=true && PID=$(cat ${PIDFILE})
  [ -n "$PID" ]         && ps -q $PID >/dev/null 2>&1 && KJZZ_PID_RUNNING=true
  
  [ $KJZZ_PID_RUNNING == true -a $KJZZ_FILE_LOCK == true ]  && echo "$curyear-$curmon-$curday $curHHMM kjzzDownloader $G$PID$END is appending \"${curyear}/${isoweek}/${filename}\" for the next $HIGH$((secUntilNextHalf / 60))$END mm = $secUntilNextHalf s. stop it?" 1>&2 && RETURN=1
  [ $KJZZ_PID_RUNNING == true -a $KJZZ_FILE_LOCK == false ] && {
    [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && {
      echo "$curyear-$curmon-$curday $curHHMM Will NOT download music. Sleeping for the next $HIGH$((secUntilNextHalf / 60))$END mn = $secUntilNextHalf s. stop it?" | tee -a $LOG 1>&2 && RETURN=0
    } || {
      echo "$curyear-$curmon-$curday $curHHMM ERROR: kjzzDownloader $G$PID$END is running but NOT appending \"${curyear}/${isoweek}/${filename}\". stop it?" | tee -a $LOG 1>&2
      RETURN=2
    }
  }
  [ $KJZZ_PID == true -a $KJZZ_PID_RUNNING == false ]       && {
    echo "$curyear-$curmon-$curday $curHHMM WARNING: kjzzDownloader $G$PID$END detected but not running. Deleted kjzz.pid" | tee -a $LOG 1>&2
    KJZZ_PID=false
    rm ${PIDFILE}
    RETURN=4
  }
  [ $KJZZ_PID == false -a $KJZZ_FILE_LOCK == true ] && {
    # It is implied that there can be only one downloader per server. 
    # Also we proved that {filename} is locked by a process with lsof. PID cannot be null
    PID=$(pgrep -f "${filename}" | head -1)
    echo "$curyear-$curmon-$curday $curHHMM kjzz.pid $G$PID$END was missing, is appending \"${curyear}/${isoweek}/${filename}\" for the next $HIGH$((secUntilNextHalf / 60))$END mm = $secUntilNextHalf s. stop it?" | tee -a $LOG 1>&2
    echo $PID >${PIDFILE}
    RETURN=5
  }
  [ $KJZZ_PID == false -a $KJZZ_FILE_LOCK == false ] && {
    [ "${filename%%Blues*}" != "${filename}" -o "${filename%%Jazz*}" != "${filename}" ] && echo "$curyear-$curmon-$curday $curHHMM Will NOT download music." | tee -a $LOG 1>&2
    echo "$curyear-$curmon-$curday $curHHMM kjzzDownloader NOT RUNNING. start it?" | tee -a $LOG 1>&2
    # [ -f "$LOG" ] && rm $LOG
    RETURN=0
  }
  
  if [ "$COMMAND" == "--help" ]; then
    echo
    echo "schedule: using jsonSchedule=${jsonSchedule}"
    [ -f "/etc/cron.d/kjzzDownloader" ] && echo "cron:     ${g}cron enabled: ${g12}/etc/cron.d/kjzzDownloader = $(grep start /etc/cron.d/kjzzDownloader)${END}" || echo "cron:     ${y}cron missing: add this in /etc/cron.d/kjzzDownloader: ${K}* * * * *   root   /docker/BiasBuster/kjzz/kjzz.sh start${END}"
    echo "program:  previous was $prevStart '${programPrev}'"
    ${programFound} && echo "${g}program:  current is   $currentStart '${program}'${END}" || echo "${Y}program:  WARNING: program name not detected${END}"
    echo "program:  next is      $nextStart '${programNext}'"
    echo
    echo "$0 disable     disable download entirely: rm ${FLAG}"
    echo "$0 enable      enable download:           touch ${FLAG}"
    echo "$0 stop        stop current download temporarily  (will restart by itself if enabled in cron)"
    echo "$0 start       start download as per schedule     (should start by itself if enabled in cron)"
    return 0
  fi

  [ "$COMMAND" == "stop" -a $KJZZ_PID_RUNNING == true ] && pkill -TERM -P "$PID" && rm ${PIDFILE} && echo "$curyear-$curmon-$curday $curHHMM kjzz.pid $G$PID$END killed." | tee -a $LOG 1>&2 && RETURN=0
  [ "$COMMAND" == "start" -a -f "$FLAG" ] && curlDownloader $secUntilNextHalf && RETURN=0
  
  return $RETURN
}

export ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PIDFILE=${ROOT}/kjzz.pid
export LOG=${ROOT}/kjzz.out
export FLAG=${ROOT}/kjzz.start

kjzzDownloader $*

# timeout 1h curl "https://kjzz.streamguys1.com/kjzz_mp3_128" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0" -H "Accept: audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5" -H "Accept-Language: en-US,en;q=0.5" -H "Range: bytes=261876-" -H "DNT: 1" -H "Connection: keep-alive" -H "Sec-Fetch-Dest: audio" -H "Sec-Fetch-Mode: no-cors" -H "Sec-Fetch-Site: cross-site" -H "Accept-Encoding: identity" >bbb.mp3
# vi /etc/cron.d/kjzzDownloader
# SHELL=/usr/bin/bash
# PATH=/exploit/bin:/exploit/PATH/was:/exploit/PATH/profile:/exploit/PATH/PLI:/exploit/PATH/Linux:/exploit/PATH/common:/exploit/PATH/aws:/exploit/PATH/apache:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/sbin:/usr/local/bin:/snap/bin
# 0,1,30,31 * * * *   root /docker/BiasBuster/kjzz/kjzz.sh start

