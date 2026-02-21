from util.response import Response

def page_render(request, handler):

    if request.path == "/":
        file = "index.html"

    elif request.path == "/chat":
        file = "chat.html"

    elif request.path == "/change-avatar":
        file = "change-avatar.html"

    elif request.path == "/direct-messaging":
        file = "direct-messaging.html"

    elif request.path == "/drawing-board":
        file = "drawing-board.html"

    elif request.path == "/login":
        file = "login.html"

    elif request.path == "/register":
        file = "register.html"

    elif request.path == "/search-users":
        file = "search-users.html"

    elif request.path == "/set-thumbnail":
        file = "set-thumbnail.html"

    elif request.path == "/settings":
        file = "settings.html"

    elif request.path == "/test-websocket":
        file = "test-websocket.html"

    elif request.path == "/upload":
        file = "upload.html"

    elif request.path == "/video-call":
        file = "video-call.html"

    elif request.path == "/video-call-room":
        file = "video-call-room.html"

    elif request.path == "/videotube":
        file = "videotube.html"

    elif request.path == "/view-video":
        file = "view-video.html"

    with open("public/layout/layout.html", "r") as f:
        layout = f.read()
    with open("public/" + file, "r") as f:
        webpage = f.read()

    html = layout.replace("{{content}}", webpage)

    res = Response()
    res.text(html)
    res.content_type = "text/html"
    handler.request.sendall(res.to_data())