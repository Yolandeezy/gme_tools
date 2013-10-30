#! /usr/bin/env python
import datetime
import time
import sys
import os.path
import json
import httplib2
import oauth2client.client
import glob
import csv
import datetime


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
    logcolumns = ["time", "name", "status", "id", "tags", "msg"]

    def log(self, clear=False, **kw):
        if clear:
            self.lastlog = {}
        kw["time"] = datetime.datetime.now().strftime("%-Y-%m-%d %H:%M:%S")
        if "tags" in kw: kw['tags'] = ", ".join(kw["tags"])
        self.lastlog.update(kw)
        self.logfile.writerow(self.lastlog)
        print ", ".join("%s=%s" % (name, self.lastlog.get(name, "")) for name in self.logcolumns)

    def request(self, url, as_json=True, raise_errors=True, retries=3, **kw):
        while retries:
            retries -= 1
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
            if response['status'] < 200 or response['status'] > 299:
                if retries:
                    self.log(status="retry")
                    continue
                elif raise_errors:
                    raise RequestException(response, content, url, kw)
            return response, content

    def connect(self):
        with file(os.path.expanduser(self.kw.get('key', 'key.p12')), 'rb') as key_file:
            key = key_file.read()
        credentials = oauth2client.client.SignedJwtAssertionCredentials(
            self.kw['email'], key, scope=self.kw.get("api", "https://www.googleapis.com/auth/mapsengine"))
        self.http = httplib2.Http()
        self.http = credentials.authorize(self.http)

    def upload (self, file):
        info = {
                "name": os.path.splitext(os.path.split(file)[1])[0],
                "description": self.kw.get("description", ""),
                "files": [{"filename": os.path.split(file)[1]}],
                "acquisitionTime": self.kw.get("time", datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
                "sharedAccessList": self.kw.get("acl", "Map Editors"),
                "attribution": self.kw["attribution"],
                "tags": "tags" in self.kw and self.kw["tags"].split(",") or [],
                "processingType": "autoMask"
                }

        for path in (os.path.join(os.path.split(file)[0], "__directory__.info"),
                     os.path.splitext(file)[0] + ".info"):
            if os.path.exists(path):
                with open(path) as f:
                    fileinfo = f.read()
                fileinfo = json.loads(fileinfo)
                for key, value in fileinfo.iteritems():
                    if isinstance(value, list):
                        info[key] += value
                    else:
                        info[key] = value

        self.log(clear=True, status="begin", **info)

        response, content = self.request(
            "https://www.googleapis.com/mapsengine/create_tt/rasters/upload?projectId=%s" % self.kw['projectid'], method="POST", body = info)
        self.image_id = str(content['id'])

        self.log(status="container", id=self.image_id)

        with open(file) as f:
            response, content = self.request(
                "https://www.googleapis.com/upload/mapsengine/create_tt/rasters/%s/files?filename=%s" % (self.image_id, os.path.split(file)[1]),
                method="POST",
                as_json=False,
                body = f.read())

        self.log(status="done")
	
    def __init__(self, *files, **kw):
        with open("mapsengine.log", "w") as f:
            self.logfile = csv.DictWriter(f, self.logcolumns, extrasaction="ignore")

            self.kw = kw

            self.connect()

            for pattern in files:
                for file in glob.glob(os.path.expanduser(pattern)):
                    try:
                        self.upload(file)
                    except Exception, e:
                        self.log(status="error", msg=str(e))
		
		


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

Uploads a raster images. Patterns can be used to select multiple files, like '*.tiff'

Available options:

--projectid=CID                                    Maps Engine project ID (not API project id!)
--attribution=ATTR                                 Name of an existing attribution
--email=USER@developer.gserviceaccount.com         Authentication name
--key=filename.p12                                 Authentication key
--api=https://www.googleapis.com/auth/mapsengine   API endpoint
--description=DESCRIPTION                          Description of resource
--time=1970-01-01T00:00:00                         Resource acquisition time
--acl=Map Editors                                  Access control for resource
--attribution=Public Domain                        Resource copyright
--tags=tag1,tag2...                                Tags for resource
"""
else:
    Command(*files, **keywords)
