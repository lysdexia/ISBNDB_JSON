#!/usr/bin/env python
import urllib2, urllib, json
import xml.etree.cElementTree as ET

class Query(object):

    def isbndb(self, query):
        self.remote_error = None
        args = urllib.urlencode(query)
        request = urllib2.Request(isbndb, args)
        response = None
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError as error:
            self.remote_error = error
            self.remote_error = error.msg
            self.code = error.code
            self.url = error.url
        return response

    
    def isbn(self, isbn, results=None):
        query = { 
            "index1": "isbn",
            "access_key": access_key,
            "value1": isbn,
            }
        if results:
            query["results"] = results
        return self.isbndb(query)

class Book(object):

    # for results w/o nested pricing
    def flat_results(self, response):
        if not response:
            return
        try:
            xml_obj = ET.fromstring(response)
        except:
            return
        for parent, child in self._iterparent(xml_obj):
            for item in parent.items():
                setattr(self, item[0], item[1])
            setattr(self, child.tag, child.text)
            for item in child.items():
                setattr(self, item[0], item[1])

    def json(self):
        _json = {}
        for i in self.__dict__:
            _json[i] = self.__dict__[i]
        return json.dumps(_json)
        
    def _iterparent(self, tree):
        for parent in tree.getiterator():
            for child in parent:
                yield parent, child

if __name__ == "__main__":

    access_key = "XXXXXXXX"
    isbndb = "http://isbndb.com/api/books.xml"

    books = {
        "propy": "0596000855",
        }
    
    for b in books:
        book = Book()
        for i in ["details", "texts"]:
            q = Query()
            book.flat_results(q.isbn(books[b], i))
            print (book.json())
