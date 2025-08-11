version = "1.1.7"
import socket
import os
import string
import sys

py_version = string.split(sys.version, ' ')[0]

STOP_FILE = "pyhttp.stop"

def listdir(path):
    try:
        names = os.listdir(path)
    except:
        return "<html><body><h1>Can't list directory</h1></body></html>"
    names.sort()
    r = "<html><body><h1>Directory listing</h1><ul>"
    for name in names:
        r = r + '<li><a href="/' + name + '">' + name + '</a></li>'
    r = r + "</ul></body></html>"
    return r

def readfile(path):
    try:
        f = open(path, "rb")
        data = f.read()
        f.close()
        return data
    except:
        return None

def content_type_from_path(path):
    # very basic mime type detection based on extension
    dot = string.rfind(path, ".")
    if dot == -1:
        return "application/octet-stream"
    ext = path[dot:]
    if ext == ".html" or ext == ".htm":
        return "text/html"
    if ext == ".txt":
        return "text/plain"
    if ext == ".jpg":
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    return "application/octet-stream"

def serve(conn, path):
    try:
        req = conn.recv(1024)
        if not req:
            return
        # req is a string in python 1.x, no decode needed
        parts = string.split(req, "\r\n")
        if len(parts) < 1:
            return
        first = parts[0]
        words = string.split(first)
        if len(words) < 2:
            return
        method = words[0]
        target = words[1]

        if target == "/":
            index = path + "/index.html"
            try:
                f = open(index)
                f.close()
                target = "/index.html"
            except:
                pass

        full = path + "/" + target[1:]
        try:
            st = os.stat(full)
        except:
            st = None

        if st and (st[0] & 0o170000) == 0o040000:  # directory check in old python (S_IFDIR)
            body = listdir(full)
            header = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
            conn.send(header + body)
        else:
            data = readfile(full)
            if data:
                ctype = content_type_from_path(full)
                header = "HTTP/1.0 200 OK\r\nContent-Type: %s\r\n\r\n" % ctype
                # conn.send needs string, data is binary, in python1, strings are bytes, so send directly
                conn.send(header + data)
            else:
                body = "404 Not Found"
                header = "HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\n"
                conn.send(header + body)
        print "Visited:", target
    except:
        print "Error in request"

def main():
    print "PyHTTP", version, "on Python", python_version
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = string.atoi(sys.argv[1])
        except:
            port = 8000

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(1)
        # no settimeout in python 1.x socket, so just block on accept

        print "Serving on port", port
        print "To stop the server, create a file named 'pyhttp.stop'"

        while 1:
            if os.path.exists(STOP_FILE):
                print "Server stopped"
                os.remove(STOP_FILE)
                break
            conn, addr = s.accept()
            serve(conn, os.getcwd())
            conn.close()
    except:
        print "Server error"
        sys.exit(1)

main()
