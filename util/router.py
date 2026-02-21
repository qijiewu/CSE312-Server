from util.response import Response

class Router:

    def __init__(self):
        self.router = []

    def add_route(self, method, path, action, exact_path=False):
        self.router.append((method, path, action, exact_path))

    def route_request(self, request, handler):
        for line in self.router:
            method = line[0]
            path = line[1]
            action = line[2]
            exact_path = line[3]
            if request.method == method:
                if exact_path:
                    if request.path == path:
                        action(request, handler)
                        return
                else:
                    if request.path.startswith(path):
                        action(request, handler)
                        return
        res = Response()
        res.status_code = 404
        res.status_text = "Not Found"
        handler.request.sendall(res.to_data())