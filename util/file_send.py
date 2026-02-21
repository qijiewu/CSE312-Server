from util.response import Response

def file_send(request, handler):

    file_path = request.path[1:]

    if file_path.endswith(".jpg"):
        content_type = "image/jpeg"
    elif file_path.endswith(".ico"):
        content_type = "image/x-icon"
    elif file_path.endswith(".gif"):
        content_type = "image/gif"
    elif file_path.endswith(".webp"):
        content_type = "image/webp"
    elif file_path.endswith(".js"):
        content_type = "text/javascript"
    elif file_path.endswith(".css"):
        content_type = "text/css"
    elif file_path.endswith(".html"):
        content_type = "text/html"

    with open(file_path, "rb") as f:
        file = f.read()

    res = Response()
    res.bytes(file)
    res.content_type = content_type

    handler.request.sendall(res.to_data())