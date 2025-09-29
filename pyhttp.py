version = "1.2.6"

import socket
import os
import string
import sys
import thread

py_version = string.split(sys.version, ' ')[0]

STOP_SERVER = False

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
    ext_map = {
        ".html": "text/html",
        ".htm": "text/html",
        ".txt": "text/plain",
        ".css": "text/css",
        ".py": "text/x-python",
        ".pyz": "text/x-python",
        ".pl": "text/x-perl",
        ".rb": "text/x-ruby",
        ".ini": "text/x-ini",
        ".inf": "text/x-inf",
        ".nfo": "text/x-nfo",
        ".md": "text/markdown",
        ".rst": "text/x-rst",
        ".jad": "text/vnd.sun.j2me.app-descriptor",
        ".c": "text/x-c",
        ".cpp": "text/x-c++src",
        ".cc": "text/x-c++src",
        ".cxx": "text/x-c++src",
        ".java": "text/x-java-source",
        ".vbs": "text/vbscript",
        ".as": "text/x-actionscript",
        ".swf": "application/x-shockwave-flash",
        ".swc": "application/x-shockwave-flash",
        ".js": "application/javascript",
        ".json": "application/json",
        ".jar": "application/java-archive",
        ".xml": "application/xml",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".ico": "image/x-icon",
        ".svg": "image/svg+xml",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".avi": "video/x-msvideo",
        ".pdf": "application/pdf",
        ".sh": "application/x-sh",
        ".command": "application/x-sh",
        ".zip": "application/zip",
        ".tar": "application/x-tar",
        ".zst": "application/zst",
        ".deb": "application/x-deb",
        ".nupkg": "application/zip",
        ".dmg": "application/x-apple-diskimage",
        ".7z": "application/x-7z-compressed",
        ".php": "application/x-httpd-php",
        ".xz": "application/x-xz",
        ".gz": "application/gzip",
        ".rar": "application/vnd.rar",
        ".exe": "application/vnd.microsoft.portable-executable",
        ".msi": "application/x-msi"
    }
    dot = string.rfind(path, ".")
    if dot == -1:
        return "application/octet-stream"
    ext = path[dot:].lower()
    return ext_map.get(ext, "application/octet-stream")

def serve(conn, path):
    try:
        req = conn.recv(1024)
        if not req:
            return
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

        if st and (st[0] & 0o170000) == 0o040000:  # directory
            body = listdir(full)
            header = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
            conn.send(header + body)
        else:
            data = readfile(full)
            if data:
                ctype = content_type_from_path(full)
                header = "HTTP/1.0 200 OK\r\nContent-Type: %s\r\n\r\n" % ctype
                conn.send(header + data)
            else:
                body = "<html><body><h1>404 Not Found</h1></body></html>"
                header = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                conn.send(header + body)
        print "Visited:", target
    except:
        print "Error in request"
    finally:
        conn.close()

def serve_thread(conn, path):
    serve(conn, path)

def main():
    port = 8000

if sys.version[0] != '1':
    msg = "PyHTTP is intended to run on Python 1.x.\n" \
          "To use, run this on Python 1.5 or newer (running on Python {}.x).".format(sys.version[0])
    try:
        print(msg)  # Python 3.x
    except:
        print msg  # Python 2.x
    sys.exit(1)  # Stop server
    if len(sys.argv) > 1:
        try:
            port = string.atoi(sys.argv[1])
        except:
            port = 8000

    print "PyHTTP", version, "on Python", py_version
    print "Serving on port", port

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(5)  # allow backlog of 5 connections

        while 1:
            try:
                conn, addr = s.accept()
                # Spawn a new thread for each client
                thread.start_new_thread(serve_thread, (conn, os.getcwd()))
            except KeyboardInterrupt:
                print "\nServer stopped by Ctrl+C"
                break
    except:
        print "Server error"
        sys.exit(1)

main()
