<html>
    <head>
        <title>Core Webserver</title>

        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />

        <link rel="stylesheet" href="/core/css/core.css">
        <style>

        iframe {
            height: 250px;
            width: 100%;

            border: 1px solid black;
        }


        </style>
        
        <script type='module'>
import { Log } from '/core/js/libUtl.js';

function OnLoad()
{
    Log('Loaded');
}

document.addEventListener('DOMContentLoaded', OnLoad);
        </script>

    </head>

    <body>


<?

for product in GetProductList():
    if product != "core":
        self.write("<a href='/%s/index.pyp'>%s</a> " % (product, product))

?>

<hr>

<br/>

<iframe src="mon.html" frameborder="0" scrolling="no"></iframe>
<iframe src="db.html" frameborder="0" scrolling="no"></iframe>


    </body>
</html>













