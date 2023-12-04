// console.log('start', history.state);

const player = new OpenPlayerJS('player', {
  controls: {
      alwaysVisible: false,
      layers: {
          left: ['play', 'time', 'volume'],
          middle: ['progress'],
          right: ['captions', 'settings', 'fullscreen'],
      }
  },
  detachMenus: false,
  forceNative: true,
  // mode: 'fill',
  // mode: 'fit',
  mode: 'responsive',
  hidePlayBtnTimer: 350,
  step: 0,
  startVolume: 1,
  startTime: 0,
  showLoaderOnInit: false,
  onError: (e) => console.error(e),
  defaultLevel: null,
  live: {
      showLabel: true,
      showProgress: false,
  },
  dash: {
      // Possible values are SW_SECURE_CRYPTO, SW_SECURE_DECODE, HW_SECURE_CRYPTO, HW_SECURE_CRYPTO,
      // HW_SECURE_DECODE, HW_SECURE_ALL
      robustnessLevel: null,
      // object containing property names corresponding to key system name strings (e.g. "org.w3.clearkey") and
      // associated values being instances of ProtectionData
      // (http://vm2.dashif.org/dash.js/docs/jsdocs/MediaPlayer.vo.protection.ProtectionData.html)
      drm: null,
  },
  flv: {
      // all FLV options available at https://github.com/bilibili/flv.js/blob/master/docs/api.md#mediadatasource
  },
  hls: {
      // all HLS options available at https://github.com/video-dev/hls.js/blob/master/docs/API.md#fine-tuning.
  },
  progress: {
      duration: 0,
      showCurrentTimeOnly: false
  },
  width: 0,
  height: 0,
  pauseOthers: true,
});
player.init();


function stem(file) {
  return file.substr(0, file.lastIndexOf('.'));
}

// OpenPlayerJS
// https://github.com/openplayerjs/openplayerjs/blob/master/docs/
// https://www.npmjs.com/package/openplayerjs
function play(sound) {
  // console.log('captions',captions);
  let id = document.querySelector('.op-player').id;
  // console.log('id',id);
  let player = OpenPlayerJS.instances[id];
  // console.log('player',player);
  let captions = stem(sound) + '.vtt';

  player.src = { src: sound };
  player.addCaptions({ src: captions, kind: "subtitles", srclang: "en", label: "English" });
  
  // https://developer.mozilla.org/en-US/docs/Web/Events#media
// https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track
  let track = document.querySelector("track").track;
  // console.log('track',track);

  // https://developer.mozilla.org/en-US/docs/Web/API/TextTrack/mode
  // cannot get this CC enabled no matter what so here is the question: https://stackoverflow.com/questions/77581173/openplayerjs-how-to-enable-track-captions-on-event
  // track.mode = "showing";
  // temporary solution: simulate click by the user...
  document.querySelector('.op-controls__captions').click();

  player.play();
  
  // https://developer.mozilla.org/en-US/docs/Web/API/History/pushState
  // history.pushState({ url: document.URL, playing: true }, "", "index.html");
  // console.log('before', history.state);
  // location.reload();
  // console.log('after', history.state);

  // <source src='file.mp3' type="audio/mp3" />
  // <track src="file.vtt" kind="subtitles" srclang="en" label="English" />
}

// console.log('end', history.state);
