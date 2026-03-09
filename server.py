import socketserver
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
from util.public_path import public_path
from util.render import page_render
from util.chat import create_chat, get_chat, update_chat, delete_chat, add_reaction, delete_reaction
from util.auth import registration, login, logout, get_profile, search_user, update_profile, enable_totp, auth_github, auth_callback


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)
        # TODO: Add your routes here
        self.router.add_route("GET", "/public", public_path, False)

        self.router.add_route("GET", "/", page_render, True)
        self.router.add_route("GET", "/login", page_render, True)
        self.router.add_route("GET", "/change-avatar", page_render, True)
        self.router.add_route("GET", "/chat", page_render, True)
        self.router.add_route("GET", "/direct-messaging", page_render, True)
        self.router.add_route("GET", "/drawing-board", page_render, True)
        self.router.add_route("GET", "/register", page_render, True)
        self.router.add_route("GET", "/search-users", page_render, True)
        self.router.add_route("GET", "/set-thumbnail", page_render, True)
        self.router.add_route("GET", "/settings", page_render, True)
        self.router.add_route("GET", "/test-websocket", page_render, True)
        self.router.add_route("GET", "/upload", page_render, True)
        self.router.add_route("GET", "/video-call", page_render, True)
        self.router.add_route("GET", "/video-call-room", page_render, True)
        self.router.add_route("GET", "/videotube", page_render, True)
        self.router.add_route("GET", "/view-video", page_render, True)

        self.router.add_route("POST", "/api/chats", create_chat, True)
        self.router.add_route("GET", "/api/chats", get_chat, True)
        self.router.add_route("PATCH", "/api/chats", update_chat, False)
        self.router.add_route("DELETE", "/api/chats", delete_chat, False)
        self.router.add_route("PATCH", "/api/reaction", add_reaction, False)
        self.router.add_route("DELETE", "/api/reaction", delete_reaction, False)

        self.router.add_route("POST", "/register", registration, True)
        self.router.add_route("POST", "/login", login, True)
        self.router.add_route("GET", "/logout", logout, True)

        self.router.add_route("GET", "/api/users/@me", get_profile, True)
        self.router.add_route("GET", "/api/users/search", search_user, False)
        self.router.add_route("POST", "/api/users/settings", update_profile, False)
        self.router.add_route("POST", "/api/totp/enable", enable_totp, True)
        self.router.add_route("GET", "/authgithub", auth_github, False)
        self.router.add_route("GET", "/authcallback", auth_callback, False)


        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
