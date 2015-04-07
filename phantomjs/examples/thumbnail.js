var page = require('webpage').create();
page.open('http://disney.wikia.com/wiki/Elsa_the_Snow_Queen', function() {
  page.zoomFactor = 0.10;
  page.render('elsa.png');
  phantom.exit();
});
