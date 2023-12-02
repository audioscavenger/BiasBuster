var links = document.querySelectorAll("a.prevWeek, a.nextWeek"); 
var linkReport = [];
var linksChecked=0;

links.forEach(function(link){
    var reportLine = {url: link.getAttribute('href'), status:0, redirectedTo: "", message : "", element : link};
    linkReport.push(reportLine);

    // console.log("HEAD " + reportLine.url);

    fetch(reportLine.url, {
      method: 'HEAD',
      mode: 'cors',
      //mode: 'no-cors',
      redirect: 'follow'
    })
    .then(function(response) {
      linksChecked++;
      reportLine.status=response.status;
      reportLine.message= response.statusText + " | " + 
                          response.type + " | " + 
                          (response.message || "") + " | " +
                          JSON.stringify(response.headers) ;
      if(response.redirected){
          reportLine.redirectedTo = response.url;
      }
      // console.table(response);
      if(!response.ok){
        // console.log(response);
        reportLine.element.style.display = 'none';
      }
    })
    .catch(function(error){
        reportLine.message = error;
        console.table(error);
        linksChecked++;
    });

});

// image modal ///////////////////////////////////////////////
function showModal(img) {
  // TODO: add parameter = img for the img to show
  document.getElementById("modal-img").src = img;
  document.getElementById("modal-root").style.display = 'inherit';
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
  zoom = document.getElementById("zoom");

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
