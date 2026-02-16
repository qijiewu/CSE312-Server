class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        split = request.split(b"\r\n\r\n", 1)
        header = split[0]
        if len(split) > 1:
            body = split[1]
            self.body = body

        str_header = header.decode()
        split_header = str_header.split("\r\n")

        request_split = split_header[0].split()
        if len(request_split) >= 3:
            self.method = request_split[0]
            self.path = request_split[1]
            self.http_version = request_split[2]

        for line in split_header[1:]:
            if ":" in line:
                line_split = line.split(":", 1)
                key, value = line_split[0].strip(), line_split[1].strip()
                self.headers[key] = value
                if key.lower() == "cookie":
                    cookie_split = value.split(";") #cookie_split = [key=value, key1=value]
                    for cookie in cookie_split:
                        if "=" in cookie:
                            pair = cookie.split("=", 1) #pair = [key, value]
                            self.cookies[pair[0].strip()] = pair[1].strip()








def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct


if __name__ == '__main__':
    test1()
