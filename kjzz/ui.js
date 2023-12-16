var links = []; 
// var links = document.querySelectorAll("a.prevWeek, a.nextWeek"); 
var linkReport = [];
var linksChecked=0;

links.forEach(function(link){
    var reportLine = {url: link.getAttribute('href'), status:0, redirectedTo: "", message : "", element : link};
    linkReport.push(reportLine);

    // console.debug("HEAD " + reportLine.url);

    fetch(reportLine.url, {
      method: 'HEAD',
      action: 'cors',
      //action: 'no-cors',
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
        // console.debug(response);
        reportLine.element.style.display = 'none';
      }
    })
    .catch(function(error){
        reportLine.message = error;
        console.table(error);
        linksChecked++;
    });

});


function updateNavBar(elem) {
  // console.debug(elem);
  const timeout = 100;
  const template = document.querySelector("#navBar");
  const templateHtml = template.innerHTML.toString().trim().replaceAll('{{','${').replaceAll('}}','}');
  const navBar = document.querySelector('.navBar');
  const swapSchedule = document.querySelector('#swapSchedule');
  
  let weekNumber  = parseInt(swapSchedule.dataset.week);
  let flip        = swapSchedule.dataset.action;
  let prevWeek    = weekNumber - 1;
  let nextWeek    = weekNumber + 1;
  let dataFlip    = { bySegment: { byChunk: 'byChunk', bySegment: 'bySegment' }, byChunk: { byChunk: 'bySegment', bySegment: 'byChunk' } };
  
  switch (elem.dataset.action) {
    case 'prevWeek':
      dataValues = {prevWeek: prevWeek-1, weekNumber: weekNumber-1, nextWeek: nextWeek-1};
      data = Object.assign({}, {flip: flip}, dataFlip[flip], dataValues);
      break;
    case 'nextWeek':
      dataValues = {prevWeek: prevWeek+1, weekNumber: weekNumber+1, nextWeek: nextWeek+1};
      data = Object.assign({}, {flip: flip}, dataFlip[flip], dataValues);
      break;
    // flip case:
    default:
      flip = dataFlip.byChunk[swapSchedule.dataset.action];
      dataValues = {prevWeek: prevWeek, weekNumber: weekNumber, nextWeek: nextWeek};
      data = Object.assign({}, {flip: flip}, dataFlip[flip], dataValues);
      break;
  }
  
  setTimeout(function() {
    html = interpolate(templateHtml, data);
    // console.debug('templateHtml',templateHtml);
    // console.debug('data',data);
    // console.debug('html',html);
    navBar.innerHTML = html;
  }, timeout);
  
}

function interpolate(template, params) {
  // https://stackoverflow.com/questions/64454284/how-to-use-html-template-with-variables-with-vanilla-js
  const replaceTags = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '(': '%28', ')': '%29' };
  const safeInnerHTML = text => text.toString().replace(/[&<>\(\)]/g, tag => replaceTags[tag] || tag);
  const keys = Object.keys(params);
  const keyVals = Object.values(params).map(safeInnerHTML);
  return new Function(...keys, `return \`${template}\``)(...keyVals);
}
 
// alternatively, we could use a listener: but it does not work at all for some reason
// el = document.querySelector('.navbar')
// el = document.querySelector('.prevWeek')
// swapSchedule.addEventListener("mouseup", function(event){
// const swapSchedule = document.getElementById("swapSchedule");
// const iframe = document.getElementById("iframe");
// iframe.contentWindow.addEventListener("load", () => {
  // console.debug('contentWindow:');
  // swapWordRecurse(document.querySelector('.navbar'), 'byChunk', 'bySegment');
// });
// iframe.contentWindow = function(event) {
  // console.debug('contentWindow:',event);
  // swapWordRecurse(document.querySelector('.navbar'), 'byChunk', 'bySegment');
// }
// iframe.addEventListener("load", function(event){
  // console.debug('event:',event);
  // swapWordRecurse(document.querySelector('.navbar'), 'byChunk', 'bySegment');
// }, true);

/* 
function swapNavBar(action, noDelay=false) {
  let navBar = document.querySelector('.navbar');
  let prevWeek = document.querySelector('.prevWeek');
  let center = document.querySelector('.center');
  let nextWeek = document.querySelector('.nextWeek');

  // BUGFIX: we need a delay before changing the links of the new links will be loaded instead.
  // there is no other way and this took me 1.5h to figure out
  let timeout = 100;
  if (noDelay) {timeout = 0}
  setTimeout(function() {
    switch (action) {
      case 'prevWeek':
        swapWordRecurse(prevWeek, 'replace', (prevWeek.dataset.week), (prevWeek.dataset.week-1));
        // prevWeek.href = swapWord(prevWeek.href, '/', (prevWeek.dataset.week), (prevWeek.dataset.week-1));
        swapWordRecurse(center,   'replace', (center.dataset.week), (center.dataset.week-1));
        swapWordRecurse(nextWeek, 'replace', (nextWeek.dataset.week), (center.dataset.week));
        // nextWeek.href = swapWord(nextWeek.href, '/', (nextWeek.dataset.week), (center.dataset.week));
        break;
      case 'nextWeek':
        swapWordRecurse(prevWeek, 'replace', (prevWeek.dataset.week), (prevWeek.dataset.week-1));
        // prevWeek.href = swapWord(prevWeek.href, '/', (prevWeek.dataset.week), (prevWeek.dataset.week-1));
        swapWordRecurse(center,   'replace', (center.dataset.week), (center.dataset.week+1));
        swapWordRecurse(nextWeek, 'replace', (nextWeek.dataset.week), (nextWeek.dataset.week+1));
        // nextWeek.href = swapWord(nextWeek.href, '/', (nextWeek.dataset.week), (nextWeek.dataset.week+1));
        break;
      case 'switch':
        swapWordRecurse(navBar, 'swap', 'bySegment', 'byChunk');
        break;
    }
  }, timeout);
}
*/

/* 
function swapWordRecurse(element, action, word1, word2) {
  console.debug('element:',element)
  console.debug('element.childNodes:',element.childNodes)
  
  // first, let's take care of parent link to replace
  if (action == 'replace' && element.href && element.dataset.week) {
    element.href = element.href.replace(word1, word2);
    element.dataset.week = word2;
    }
  for (let node of element.childNodes) {
    console.debug(node);
    switch (node.nodeType) {
      case Node.ELEMENT_NODE:
        console.debug(action, 'ELEMENT_NODE:', node)
        if (node.href) {
          if (action == 'replace') {
            node.href = swapWord(node.href, '/', word1, word2);
            if (node.dataset.week) node.dataset.week = word2;
          } else {
            node.href = swapWord(node.href, '/', word1, word2);
            if (node.dataset.week) node.dataset.week = word2;
          }
        }
        swapWordRecurse(node, action, word1, word2);
        break;
      case Node.TEXT_NODE:
        console.debug(action, 'TEXT_NODE:', node)
        if (node.textContent) { node.textContent = swapWord(node.textContent, ' ', word1, word2); }
        break;
      case Node.DOCUMENT_NODE:
        console.debug(action, 'DOCUMENT_NODE:', node)
        swapWordRecurse(node, action, word1, word2);
    }
    
  }
  return true;
}
*/

/* 
function swapWord(str, sep, word1, word2) {
  console.debug('before:', str)
  let words = str.split(sep);
  for (var i = 0, len = words.length; i < len; i++) {
    if (words[i].match(word1)) {
      words[i] = words[i].replace(word1, word2);
    } else {
      words[i] = words[i].replace(word2, word1);
    }
  }
  console.debug('after: ', words.join(sep))
  return words.join(sep); 
}
*/

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