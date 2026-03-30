import socketserver
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
from util.public_path import public_path
from util.render import page_render
from util.chat import create_chat, get_chat, update_chat, delete_chat, add_reaction, delete_reaction
from util.auth import registration, login, logout, get_profile, search_user, update_profile, enable_totp, auth_github, auth_callback
from util.avatar import update_avatar
from util.video import upload_video, get_videos, get_video, set_thumbnail

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
        self.router.add_route("GET", "/settings", page_render, True)
        self.router.add_route("GET", "/test-websocket", page_render, True)
        self.router.add_route("GET", "/upload", page_render, True)
        self.router.add_route("GET", "/video-call", page_render, True)
        self.router.add_route("GET", "/video-call-room", page_render, True)
        self.router.add_route("GET", "/videotube", page_render, True)
        self.router.add_route("GET", "/videotube/upload", page_render, True)
        self.router.add_route("GET", "/videotube/videos", page_render, False)
        self.router.add_route("GET", "/videotube/set-thumbnail", page_render, False)

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

        self.router.add_route("POST", "/api/users/avatar", update_avatar, False)

        self.router.add_route("POST", "/api/videos", upload_video, True)
        self.router.add_route("GET", "/api/videos", get_videos, True)
        self.router.add_route("GET", "/api/videos/", get_video, False)
        self.router.add_route("PUT", "/api/thumbnails/", set_thumbnail, False)

        super().__init__(request, client_address, server)

    def handle(self):
        received_data = b""
        while b"\r\n\r\n" not in received_data:
            received_data += self.request.recv(2048)
        data_split = received_data.split(b"\r\n\r\n", 1)
        header = data_split[0]
        if len(data_split) > 1:
            body = data_split[1]
        else:
            body = b""
        header_decode = header.decode()
        header_split = header_decode.split("\r\n")
        content_length = 0
        for line in header_split:
            if line.lower().startswith("content-length"):
                length_split = line.split(":", 1)
                content_length = int(length_split[1].strip())
        while len(body) < content_length:
            body += self.request.recv(2048)

        received_data = header + b"\r\n\r\n" + body
        print(self.client_address)
        print("--- received data ---")
        #print(received_data)
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
