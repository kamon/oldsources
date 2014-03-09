# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
import csv
import time

def exportContentsToCSV(context, path, item_type, filter=None):
    """
    get a csv with partners from context.
    """

    portal_catalog = getToolByName(context, 'portal_catalog')

    text = StringIO()
    writer = csv.writer(text, csv.excel, delimiter=';')

    # First, i look for the items' fields
    # Default case is for Stations-service & Restaurants
    items_fields = ["id",
                    "title",
                    "address",
                    #"extra_address",
                    "city",
                    "zip",
                    #"country",
                    "state",
                    'contactName',
                    'privatePhone',
                    "phone",
                    "fax",
                    "email",
                    #"email2",
                    #"email3",
                    "web",
                    "text",
                    ]
                    
    #if item_type == 'JubinRestaurantPartner':
    #    items_fields = ...
    
    # Case for Commerces
    if item_type == 'JubinCommercialPartner':
        items_fields = items_fields + ['reduction', 'reductionConditions']

    # I add them to the first row in the CSV
    writer.writerow(items_fields)

    # I now get all organizations from the given path using the filter
    export_content_types = ['JubinStationPartner',
                            'JubinRestaurantPartner',
                            'JubinCommercialPartner'
                            ]
    if filter:
        all_items =[i.getObject() for i in portal_catalog(
                                    portal_type = export_content_types,
                                    path = path,
                                    id = {'query':filter,
                                          'operator':'or'}
                                    )]
                                    
    # If no filter is given, i intend to export all persons.
    else:
        all_items =[i.getObject() for i in portal_catalog(
                                    portal_type = export_content_types,
                                    path = path
                                    )]

    # And now, for each organization, i load his data on each column
    for item in all_items:
        row = []
        for field in items_fields:
            v = getattr(item,field, '')
            row.append(v)

        writer.writerow(row)

    return text


def setCSVHeaders(request, text, export_type):
    """
    This function will set the request apropiately to return a csv file
    """
    request.RESPONSE.setHeader('Content-Type','application/csv;charset=utf-8') # or use cp1252 ?
    request.RESPONSE.setHeader('Content-Length',len(text.getvalue()))
    request.RESPONSE.setHeader('Content-Disposition',
                               'inline;filename=%s-%s.csv' %(
                               export_type,
                               time.strftime("%Y%m%d-%H%M%S",time.localtime())))

    return request


def exportContents(context, request, path, filter=None, format='csv'):
    """
    This function will first get the exported organizations, and will load the RESPONSE headers apropiately to return it to the browser and get a nice download dialog.
    """

    # Using this dictionary we do a matching with the format chosen by the user with the apropiate function
    formats = {'csv':exportContentsToCSV,}
    # And with this other dictionary we do a matching with the format chosen and how the response header should be set.
    headers = {'csv':setCSVHeaders,}

    # We call the importer according to the format chosen by the user. If the format is not available, then a CSV export is done
    # We also handle the items' content type needed for doing the specific export
    export_selection = request.form.get('export_selection', False)
    item_type = 'JubinStationPartner'  # default
    if export_selection == 'restaurants':
        item_type = 'JubinRestaurantPartner'
    if export_selection == 'commerces':
        item_type = 'JubinCommercialPartner'
    text = formats.get(format.lower(), 'csv')(context, path, item_type, filter)

    # Finally we set the response headers so it will open a download dialog
    export_type = 'export-%s' % context.getId()
    request = headers.get(format.lower(), 'csv')(request, text, export_type)

    return text.getvalue()

