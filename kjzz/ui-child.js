// image modal ///////////////////////////////////////////////
function showModal(img) {
  // TODO: add parameter = img for the img to show
  document.getElementById("modal-img").src = img;
  document.getElementById("modal-root").style.display = 'inherit';
  // window.frames['iframe'].contentDocument.getElementById("modal-img").src = img;
  // window.frames['iframe'].contentDocument.getElementById("modal-root").style.display = 'inherit';
}

function onClickModalBackdrop(img) {
  // click anywhere to close it, even the grey backdrop
  // alert(img);
  img.parentNode.style.display = 'none';
}

function onClickImgPrevent(event) {
  // this function will prevent the closing when click on img itself so you can drag it
  //   , and still close it when click on the parent backdrop
  // alert('img');
  if (!event) var event = window.event; 
  event.cancelBubble = true;
  if (event.stopPropagation) event.stopPropagation();
}

function onClickModalCloseBtn(div) {
  // click on the X to close it
  div.parentNode.parentNode.style.display = 'none';
}
// image modal ///////////////////////////////////////////////


// image zoom ///////////////////////////////////////////////
// https://dev.to/stackfindover/zoom-image-point-with-mouse-wheel-11n3
var scale = 1,
panning = false,
pointX = 0,
pointY = 0,
start = { x: 0, y: 0 },
zoom = document.getElementById('zoom');
// zoom = window.frames['iframe'].contentDocument.getElementById('zoom');


function setTransform() {
  zoom.style.transform = "translate(" + pointX + "px, " + pointY + "px) scale(" + scale + ")";
}

zoom.onmousedown = function (e) {
  e.preventDefault();
  start = { x: e.clientX - pointX, y: e.clientY - pointY };
  panning = true;
}

zoom.onmouseup = function (e) {
  panning = false;
}

zoom.onmousemove = function (e) {
  e.preventDefault();
  if (!panning) {
    return;
  }
  pointX = (e.clientX - start.x);
  pointY = (e.clientY - start.y);
  setTransform();
}

zoom.onwheel = function (e) {
  e.preventDefault();
  var xs = (e.clientX - pointX) / scale,
    ys = (e.clientY - pointY) / scale,
    delta = (e.wheelDelta ? e.wheelDelta : -e.deltaY);
  (delta > 0) ? (scale *= 1.2) : (scale /= 1.2);
  pointX = e.clientX - xs * scale;
  pointY = e.clientY - ys * scale;

  setTransform();
}
// image zoom ///////////////////////////////////////////////


// OpenPlayerJS caller ///////////////////////////////////////////////
function play(sound) {
  let soundUrl = window.location.origin+'/kjzz/'+sound;
  console.debug('window.location',window.location)
  console.debug('window.location.origin',window.location.origin)
  console.debug('Child: sends',soundUrl)
  window.parent.postMessage({message: soundUrl}, window.location.origin);
}
// OpenPlayerJS caller ///////////////////////////////////////////////
