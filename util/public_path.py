from util.response import Response

def public_path(request, handler):

    file_path = request.path[1:]
    content_type = "text/plain; charset=utf-8"

    if file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        content_type = "image/jpeg"
    elif file_path.endswith(".ico"):
        content_type = "image/x-icon"
    elif file_path.endswith(".gif"):
        content_type = "image/gif"
    elif file_path.endswith(".webp"):
        content_type = "image/webp"
    elif file_path.endswith(".js"):
        content_type = "text/javascript; charset=utf-8"
    elif file_path.endswith(".css"):
        content_type = "text/css; charset=utf-8"
    elif file_path.endswith(".html"):
        content_type = "text/html; charset=utf-8"
    elif file_path.endswith(".png"):
        content_type = "image/png"
    elif file_path.endswith(".mp4"):
        content_type = "video/mp4"

    with open(file_path, "rb") as f:
        file = f.read()

    res = Response()
    res.bytes(file)
    res.content_type = content_type

    handler.request.sendall(res.to_data())