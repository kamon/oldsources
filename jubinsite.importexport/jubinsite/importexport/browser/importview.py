from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.contacts import contactsMessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from jubinsite.importexport.importer import importCSVPartners

import zope.i18n


class IPartnerImportView(Interface):
    """
    Import view interface
    """

class PartnerImportView(BrowserView):
    """
    Import browser view
    """
    implements(IPartnerImportView)

    pt = ViewPageTemplateFile('importview.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        submitted = self.request.form.get('import.submitted', False)

        if submitted:
            import_selection = self.request.form.get('import_selection', False)
            #print import_selection
            import_content_type = 'JubinStationPartner'  # default
            if import_selection == 'restaurants':
                import_content_type = 'JubinRestaurantPartner'
            if import_selection == 'commerces':
                import_content_type = 'JubinCommercialPartner'

            import_file = self.request.form.get('import_file')
            path = '/'.join(self.context.getPhysicalPath())


            # Call the organizations import method
            imported = importCSVPartners(self.context, path, import_file, import_content_type)
            aux = _(u'%s successfuly imported organizations')
            status = zope.i18n.translate(aux, context=self.request)

            url = self.context.absolute_url() + \
                      '/partner_import_view?message=%s' % (status%imported,)
            return self.request.response.redirect(url)
        
        return self.pt()

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
