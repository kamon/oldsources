# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, INFO, WARNING
from config import PROJECTNAME
import zope.i18n

from collective.contacts import contactsMessageFactory as _

import codecs
import csv

from jubin.site.vocabularies import normalize_name


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

def strToInt(data):
    return int(data)

def strToFloat(data):
    return float(data)

def removeExtension(filename):
    if '.' in filename:
        filename = filename[:filename.rfind('.')]

    return filename


def importCSVPartners(context, path, file, content_type):
    """
    This function is used to import partners to a given path using
    a CSV file.
    """

    aux = _("Starting the partners import process")
    msg = zope.i18n.translate(aux, context=context.request)
    LOG(PROJECTNAME, INFO, msg)
    # First we set our results as an empty list, we will be loading
    # each user here
    results = []

    portal_catalog = getToolByName(context, 'portal_catalog')

    # we first make sure the content is in utf8
    reader = UnicodeReader(file)

    # Now we first load the headers
    headers = reader.next()
    rowLength = len(headers)
    counter = 0

    # Now i have to continue loading the rest of the items
    for row in reader:
        # We now check that we have consistency in our CSV
        assert len(row) == rowLength
        result = {}
        for j in range(rowLength):
            result[headers[j]] = row[j]

        # And now, i have a new item, i add it to the results
        results.append(result)
        counter += 1

    aux = _('${items_number} partners to be added to ${location}.',\
            mapping={'items_number':counter,
                     'location':path})
    msg = zope.i18n.translate(aux, context=context.request)
    LOG(PROJECTNAME, INFO, msg)

    counter = 0
    # I now have all items in my results, so i should start adding them to site
    for item in results:
        print item
        # title
        item_title = item['title']
        if item.has_key('title_prefix'):  # if there is a prefix such as 'Restaurant' or 'Hotel-restaurant'
            item_title = "%s %s" % (item['title_prefix'], item_title)

        # id
        item_id = ''
        if item.has_key('id'):
            item_id = normalize_name(item['id'])   # we make sure we have a normalized string
        else:  # use 'title' for that
            item_id = normalize_name(item_title)

        if context.get(item_id):
            aux = _("There's already an item with this id here.")
            msg = zope.i18n.translate(aux, context=context.request)
            LOG(PROJECTNAME, WARNING, msg)

            aux = _('You will have to load the item with id '
                    '${item_id} manually.',\
                    mapping={'item_id': item_id})
            msg = zope.i18n.translate(aux, context=context.request)
            LOG(PROJECTNAME, WARNING, msg)

        else:
            try:  
                context.invokeFactory(content_type, item_id)
                obj = context.get(item_id)
                for attr in item.keys():
                    if attr == 'id':
                        continue
                    elif attr in ['title_prefix',]:  # those we do not use directly
                        continue
                    elif attr == 'title':  # case : use the value we already calculated (to take prefix into account)
                        setattr(obj, 'title', item_title)
                    elif attr == 'city':    # case : city name needs to be normalized
                        setattr(obj, attr, normalize_name(item[attr]))
                    elif attr in ['sp95', 'sp98', 'shop', 'gaz', 'diesel', 'lavage']:  # special case : boolean
                        if item[attr] in ['x', 'X']:
                            setattr(obj, attr, True)
                    else:
                        setattr(obj, attr, item[attr])
                counter += 1
                portal_catalog.reindexObject(obj)

                aux = _('Successfuly added ${item_id}.',\
                        mapping={'item_id': item_id})
                msg = zope.i18n.translate(aux, context=context.request)
                LOG(PROJECTNAME, INFO, msg)

            except:
                aux = _('There was an error while adding.')
                msg = zope.i18n.translate(aux, context=context.request)
                LOG(PROJECTNAME, WARNING, msg)

                aux = _('You will have to load the item with id '
                        '${item_id} manually.',\
                        mapping={'item_id': item_id})
                msg = zope.i18n.translate(aux, context=context.request)
                LOG(PROJECTNAME, WARNING, msg)

    aux = _('Successfuly added ${items_number} items to ${location}.',\
            mapping={'items_number':counter,
                     'location':path})
    msg = zope.i18n.translate(aux, context=context.request)
    LOG(PROJECTNAME, INFO, msg)

    return counter
