var links = document.querySelectorAll("a.prevWeek, a.nextWeek"); 
// var links = window.frames['iframe'].contentDocument.querySelectorAll("a.prevWeek, a.nextWeek"); 
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


/*
// we use css and flex instead of that
// <iframe src="frame.html" onload="resizeIframe(this)"></iframe>
function resizeIframe(iframe) {
  let detectedHeight = iframe.contentWindow.document.body.scrollHeight;
  let adjustedHeight = detectedHeight;
  iframe.height = adjustedHeight + "px";
  console.debug('parent: detectedHeight=',detectedHeight,'adjustedHeight=',adjustedHeight);
}
*/