const player = new OpenPlayerJS('audio', {
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


function play(sound) {
  var id = document.querySelector('.op-player').id;
  console.log('id',id);
  var player = OpenPlayerJS.instances[id];
  console.log('player',player);
  player.src = { src: sound };
  player.play();
}
