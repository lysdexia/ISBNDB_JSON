#!/usr/bin/env python
import urllib2, urllib, json, copy, os, ConfigParser
import xml.etree.cElementTree as ET

class Query(object):
    # query isbndb and convert output into book objects

    def isbndb_query(self, collection, query):
        # returns a list of books in object form
        self.remote_error = None
        args = urllib.urlencode(query)
        request = urllib2.Request(os.path.join(isbndb, collection), args)
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
        # Iterate over the xml object and place all values into Book object
        # Create a new book if initial book object not provided.
        if not book:
            book = DBBook()
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

    def arguments(self, style, value, results):
        query = { 
            "index1": style,
            "value1": value,
            "access_key": access_key,
            }
        if results:
            query["results"] = results
        return self.isbndb_query(self.collection, query)

class DBBook(object):

    def json(self):
        # this is a kinnard! I am using pyjson module instead
        # of python standard json otherwise:
        # return json.JSONEcoder().encode(self.__dict__)
        # will replace with correct code later
        # spit out vars in json format
        _json = {}
        for i in self.__dict__:
            _json[i] = self.__dict__[i]
        return json.dumps(_json)

class Books(Query):
    def __init__(self):
        self.query_type = "Books"
        self.collection = "books.xml"
 
class Subjects(Query):
    #Arguments: name, category_id, subject_id
    #Results: categories, structure, 
    def __init__(self):
        self.query_type = "Subjects"
        self.collection = "subjects.xml"
  
class Categories(Query):
    #Arguments: name, category_id, subject_id
    #Results: categories, structure, 
    def __init__(self):
        self.query_type = "Categories"
        self.collection = "categories.xml"

def Subjects_test():
    # TODO name and category are not returning results, investigate
    tests = [("name", ["astronomy+teaching",]),
            ("category_id", ["science.biology.history"]),
            ("subject_id", ["molecular_biology", "bioinformatics"]),
            ]
    result_types = ["categories", "structure"]
    run_tests(Subjects, tests, result_types)

def Books_test():
    test_isbn = [ "0596000855", ]
    test_title = [ "neruomancer", "artificial kid", ]
    test_combined = [ "nutshell+by+o'reilly", "sonnets+by+shakespeare", ]
    test_full = [ "lord+foul", "i+can+feel+the+heat+closing+in","case+molly+millions", ]

    tests = [
        ("isbn", test_isbn),
        ("title", test_title),
        ("combined", test_combined),
        ("full", test_full), ]

    result_types = ["prices", "details", "texts", "pricehistory", "subjects", "marc", "authors", False]

    run_tests(Books, tests, result_types)

def run_tests(Collection, tests, result_types):
    for style, values in tests:
        for value in values: 
            for results in result_types:
                q = Collection()
                books = q.arguments(style, value, results)
                for book in books:
                    print ("%s %s %s"%(style, value, results))
                    print (book.json())
                print ("%s %s"%(results, len(books)))

# testing. 
if __name__ == "__main__":

    access_key = "M9N4RWZC"
    isbndb = "http://isbndb.com/api/"
    #Books_test()
    Subjects_test()
    #Categories_test()
