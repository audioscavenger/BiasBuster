group.addEventListener('pointermove', function (evt) {
  // event target is the marker itself, group is a parent event target
  // for all objects that it contains
  console.log(`Is it working yet?`)
  var bubble =  new H.ui.InfoBubble(evt.target.getPosition(), {
    // read custom data
    content: evt.target.getData()
  });
  // show info bubble
  ui.addBubble(bubble);
}, false);

