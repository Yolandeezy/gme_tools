#! /usr/bin/env python
import datetime
import time
import sys
import os.path
import json
import httplib2
import oauth2client.client



class RequestException(Exception):
    def __init__(self, response, content, url, kw):
        self.response = response
        self.content = content
        self.url = url
        self.kw = kw
        Exception.__init__(self)
    def __unicode__(self):
        return "%s %s\n%s\n%s" % (self.response['status'], self.url, json.dumps(self.response, indent=2), json.dumps(self.content, indent=2))
    def __str__(self): return unicode(self).encode("utf-8")
    def __repr__(self): return unicode(self)

class Command(object):
    def request(self, url, as_json=True, raise_errors=True, **kw):
        kw['headers'] = dict(kw.get('headers', {}))
        if 'body' in kw and as_json:
            kw['body'] = json.dumps(kw['body'])
            kw['headers']["Content-Type"] = "application/json"
        response, content = self.http.request(url, **kw)
        try:
            content = json.loads(content)
        except:
            pass
        response['status'] = int(response['status'])
        if raise_errors:
            if response['status'] < 200 or response['status'] > 299:
                raise RequestException(response, content, url, kw)
        return response, content

    def connect(self):
        with file(self.kw.get('key', 'key.p12'), 'rb') as key_file:
            key = key_file.read()
        credentials = oauth2client.client.SignedJwtAssertionCredentials(
            self.kw['email'], key, scope=self.kw.get("api", "https://www.googleapis.com/auth/mapsengine"))
        self.http = httplib2.Http()
        self.http = credentials.authorize(self.http)

    def __init__(self, *files, **kw):
        self.files = files
        self.kw = kw

        self.connect()

        response, content = self.request(
            "https://www.googleapis.com/mapsengine/create_tt/rasters/upload?projectId=%s" % self.kw['projectid'], method="POST", body = {
                "name": self.kw.get("name", "Unnamed map"),
                "description": self.kw.get("description", ""),
                "files": [
                    { "filename": os.path.split(file)[1] }
                    for file in self.files],
                "acquisitionTime": self.kw.get("time", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
                "sharedAccessList": self.kw.get("acl", "Map Editors"),
                "attribution": self.kw["attribution"],
                "tags": "tags" in self.kw and self.kw["tags"].split(",") or [],
                "processingType": "autoMask"
                }
            )
        self.image_id = str(content['id'])
        print "Image id: " + self.image_id

        for file in self.files:
            with open(file) as f:
                print os.path.split(file)[1] + "...",
                response, content = self.request(
                    "https://www.googleapis.com/upload/mapsengine/create_tt/rasters/%s/files?filename=%s" % (self.image_id, os.path.split(file)[1]),
                    method="POST",
                    as_json=False,
                    body = f.read())
                print "DONE"


keywords = {}
files = []
for arg in sys.argv[1:]:
    if arg.startswith("--"):
        arg = arg[2:]
        value = True
        if "=" in arg:
            arg, value = arg.split("=", 1)
        keywords[arg] = value
    else:
        files.append(arg)

if not files or "help" in keywords:
    print """Usage: mapsengineupload --email=EMAIL --projectid=PROJECTID --attribution=ATTRNAME OPTIONS FILENAMES...

FILENAME can use standard wildcards e.g. '*.tiff'

Uploads a single raster image.  Specify the primary image file first, and optionally any additional supporting files

Available options:

--projectid=CID                                    Maps Engine project ID (not API project id!)
--attribution=ATTR                                 Name of an existing attribution
--email=USER@developer.gserviceaccount.com         Authentication name
--key=filename.p12                                 Authentication key
--api=https://www.googleapis.com/auth/mapsengine   API endpoint
--name=NAME                                        Resource name
--description=DESCRIPTION                          Description of resource
--time=1970-01-01T00:00:00                         Resource acquisition time
--acl=Map Editors                                  Access control for resource
--attribution=Public Domain                        Resource copyright
--tags=tag1,tag2...                                Tags for resource
"""
else:
    Command(*files, **keywords)
