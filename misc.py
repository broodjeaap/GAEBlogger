def makeLink(url,content):
    return "<a href='%s'>%s</a>" %(url,content)

def header():
    ret = """
    <html>
        <head>
            <link rel="stylesheet" href="/static/global.css"/>
            <script type='text/javascript' src='/static/jquery-1.6.4.js'></SCRIPT>
            <script type='text/javascript' src='/static/script.js'></SCRIPT>
        </head>
        <body>
            <div class='content'>
                <div class='header'>
                    <a href='/'>David van Zessen</a>
                </div>"""
    return ret

def footer():
    ret = "</div></body></html>"
    return ret