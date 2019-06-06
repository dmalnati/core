<html>
    <head>
        <title>Core Webserver</title>

        <link rel="stylesheet" href="/core/css/core.css">
        <style>

        .iframeContainer {
            position: relative;
            padding-bottom: 0%;
            padding-top: 35px;
            height: 100%;
            overflow: hidden;
        }

        .iframeContainer iframe {
            border: 0;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        </style>
        
  <link href="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css" rel="stylesheet">
  <script src="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js"></script>
  <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">

    <script>
  function resizeIframe(obj) {
    obj.style.height = obj.contentWindow.document.body.scrollHeight + 'px';
  }
    function OnLoad()
    {
        //mdc.ripple.MDCRipple.attachTo(document.querySelector('.foo-button'));
		mdc.tabBar.MDCTabBar.attachTo(document.querySelector('.mdc-tab-bar'));

        document.addEventListener("MDCTabBar:activated", function(event) {
            console.log(event.detail.index);

            idx__src = {}
<?
idx = 0
for product in GetProductList():
    self.write("idx__src[%s] = \"/%s/index.pyp\";" % (idx, product))
    idx += 1
?>

            //document.getElementById('iframe'

        });
    }
    </script>
    </head>

    <body onload='OnLoad();'>











<div class="mdc-tab-bar" role="tablist">
  <div class="mdc-tab-scroller">
    <div class="mdc-tab-scroller__scroll-area">
      <div class="mdc-tab-scroller__scroll-content">


<?

def MakeTable(name, index, selected):

    strActive = ""
    if selected:
        strActive = "mdc-tab-indicator--active"

    return \
"""
        <button class="mdc-tab mdc-tab--active" role="tab" aria-selected="%s" tabindex="%s">
          <span class="mdc-tab__content">
            <span class="mdc-tab__text-label">%s</span>
          </span>
          <span class="mdc-tab-indicator %s">
            <span class="mdc-tab-indicator__content mdc-tab-indicator__content--underline"></span>
          </span>
          <span class="mdc-tab__ripple"></span>
        </button>
""" % (selected, index, name, strActive)


idx = 0
selected = True
productList = GetProductList()
for product in productList:
	self.write(MakeTable(product, idx, selected))
	selected = False
	idx += 1

?>

      </div>
    </div>
  </div>
</div>



<div class="iframeContainer">
   <iframe id='iframe' src="core.html" frameborder="0" scrolling="no" onload="resizeIframe(this)"></iframe>
</div>










    </body>
</html>













