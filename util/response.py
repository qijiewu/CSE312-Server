import json
from email.quoprimime import header_encode


class Response:
    def __init__(self):

        self.status_code = 200
        self.status_text = 'OK'
        self.header_dict = {}
        self.cookie_dict = {}
        self.byte_body = b""
        self.content_type = None

    def set_status(self, code, text):
        self.status_code = code
        self.status_text = text
        return self

    def headers(self, headers):
        for key in headers: #headers = {key = value, key1 = value1}
            self.header_dict[key] = headers[key]
        return self

    def cookies(self, cookies):
        for key in cookies:
            self.cookie_dict[key] = cookies[key]
        return self

    def bytes(self, data):
        self.byte_body = self.byte_body + data
        return self

    def text(self, data):
        data = data.encode()
        self.byte_body += data
        return self

    def json(self, data):
        json_data = json.dumps(data)
        self.byte_body = json_data.encode()
        self.content_type = "application/json"
        return self

    def to_data(self):
        #request + header + ct, cl, ck + body
        response = "HTTP/1.1" + " " + str(self.status_code) + " " + self.status_text + "\r\n"
        #request line
        response_encoded = response.encode()

        header = ""
        for key in self.header_dict:
            header += key + ": " + str(self.header_dict[key]) + "\r\n"
        #header
        header_encoded = header.encode()

        if self.content_type:
            content_type = self.content_type
        else:
            content_type = "text/plain; charset=utf-8"
        ct = "Content-Type: " + content_type + "\r\n"
        #content type
        ct_encoded = ct.encode()

        content_length = len(self.byte_body)
        cl = "Content-Length: " + str(content_length) + "\r\n"
        #content length
        cl_encoded = cl.encode()

        set_cookie = ""
        for key in self.cookie_dict:
            set_cookie += "Set-Cookie: " + key + "=" + self.cookie_dict[key] + "\r\n"
        #set cookie
        set_cookie_encoded = set_cookie.encode()

        nosniff = "X-Content-Type-Options: nosniff\r\n"
        #sniff
        nosniff_encoded = nosniff.encode()

        blank = "\r\n"
        blank_encoded = blank.encode()

        op = response_encoded + header_encoded + ct_encoded + cl_encoded + nosniff_encoded + set_cookie_encoded + blank_encoded + self.byte_body
        return op



def test1():
    res = Response()
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()
    print("expected:", expected)
    print("actual  :", actual)


if __name__ == '__main__':
    test1()
