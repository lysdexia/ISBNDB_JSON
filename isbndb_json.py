#!/usr/bin/env python
import urllib2, urllib, json, copy
import xml.etree.cElementTree as ET

class Query(object):
    # query isbndb and convert output into book objects
 
    def isbn(self, isbn, results=None):
        # query by ISBN number
        query = { 
            "index1": "isbn",
            "access_key": access_key,
            "value1": isbn,
            }
        if results:
            query["results"] = results
        return self.isbndb(query)

    def isbndb(self, query):
        # returns a list of books in object form
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
        return self.flatten_results(response)
   
    def flatten_results(self, response):
        # Flatten all objects into multiple book/author/whatever objects
        # Will break if more than one nested type. Thus far: no more than 
        # one nested type. :-)
        books = []
        if not response:
            return books
        try:
            xml_obj = ET.fromstring(response)
        except:
            return books

        # create our initial book object
        book = self._book_obj(xml_obj)
                
        found_nested = []
        for tag in book.__dict__:
            nested = xml_obj.findall(".//%s"%tag)
            if len(nested) >1:
                found_nested = nested
        if not found_nested:
            return [book]

        for nested in found_nested:
            books.append(self._book_obj(nested, copy.deepcopy(book)))
        return books

    def _book_obj(self, xml_obj, book=None):
        # Iterate over the xml object and place all values into book object
        # Create a new book if initial book object not provided.
        if not book:
            book = Book()
        for parent, child in self._iterparent(xml_obj):
            setattr(book, parent.tag, parent.text.strip())
            for item in parent.items():
                setattr(book, item[0], item[1].strip())
            setattr(book, child.tag, child.text)
            for item in child.items():
                setattr(book, item[0], item[1].strip())
        return book
    
    def _iterparent(self, tree):
        # the usual pattern
        for parent in tree.getiterator():
            for child in parent:
                yield parent, child

class Book(object):

    def json(self):
        # spit out vars in json format
        _json = {}
        for i in self.__dict__:
            _json[i] = self.__dict__[i]
        return json.dumps(_json)
       
# testing. 
if __name__ == "__main__":

    access_key = "XXXXXXXX"
    isbndb = "http://isbndb.com/api/books.xml"

    test_books = {
        "propy": "0596000855",
        }
    
    for b in test_books:
        for i in ["prices", "details", "texts"]:
            q = Query()
            books = q.isbn(test_books[b], i)
            print ("%s %s"%(i, len(books)))
            #for book in books:
            #    if hasattr(book, "price"):
            #        print (book.json())
            #        print ("%s %s"%(book.currency_code, book.price))
