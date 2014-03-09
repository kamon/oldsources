# -*- coding: utf-8 -*-

"""Definition of the Jubin site content types
"""

from zope.interface import implements, directlyProvides
from zope.component import adapts, getMultiAdapter

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.atapi import AnnotationStorage

#from Products.ATContentTypes.content import newsitem
from Products.ATContentTypes.content import document

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

from burocom.article import siteMessageFactory as _
from burocom.article.interfaces import IBurocomArticle
from burocom.article.config import PROJECTNAME

from archetypes.multifile.MultiFileField import MultiFileField
from archetypes.multifile.MultiFileWidget import MultiFileWidget

from plone.app.blob import field as blobfield

validation.register(MaxSizeValidator('checkArticleImageMaxSize',
                                     maxsize=zconf.ATNewsItem.max_file_size))

IMAGE_VALIDATORS = (('isNonEmptyFile', V_REQUIRED),
                    ('checkArticleImageMaxSize', V_REQUIRED))

IMAGE_SIZES = {'large'   : (768, 768),
               'preview' : (400, 400),
               'mini'    : (200, 200),
               'thumb'   : (128, 128),
               'tile'    :  (64, 64),
               'icon'    :  (32, 32),
               'listing' :  (16, 16),
               }

ArticleSchema = document.ATDocumentSchema.copy() + atapi.Schema((

    #blobfield.ImageField('image',
    atapi.ImageField('image',
                     required = False,
                     storage = atapi.AnnotationStorage(migrate=True),
                     languageIndependent = True,
                     sizes = IMAGE_SIZES,
                     validators = IMAGE_VALIDATORS,
                     widget = atapi.ImageWidget(
                                             description = "Image principale",
                                             label= u'Image',
                                             show_content_type = False)
                     ),

    atapi.StringField('imageCaption',
                      required = False,
                      searchable = True,
                      widget = atapi.StringWidget(
                      description = '',
                      label = u'Légende',
                      size = 40)
        ),

    #blobfield.ImageField('image1',
    atapi.ImageField('image1',
                     required = False,
                     storage = atapi.AnnotationStorage(migrate=True),
                     languageIndependent = True,
                     sizes = IMAGE_SIZES,
                     validators = IMAGE_VALIDATORS,
                     widget = atapi.ImageWidget(
                                             description = "",
                                             label= u'Image bis',
                                             show_content_type = False)
                     ),

    atapi.StringField('image1Caption',
                      required = False,
                      searchable = True,
                      widget = atapi.StringWidget(
                      description = '',
                      label = u'Légende',
                      size = 40)
        ),

    #blobfield.ImageField('image2',
    atapi.ImageField('image2',
                     required = False,
                     storage = atapi.AnnotationStorage(migrate=True),
                     languageIndependent = True,
                     sizes = IMAGE_SIZES,
                     validators = IMAGE_VALIDATORS,
                     widget = atapi.ImageWidget(
                                             description = "",
                                             label= u'Image ter',
                                             show_content_type = False)
                     ),

    atapi.StringField('image2Caption',
                      required = False,
                      searchable = True,
                      widget = atapi.StringWidget(
                      description = '',
                      label = u'Légende',
                      size = 40)
        ),

    MultiFileField('file',
                   #primary=True,
                   languageIndependent=True,
                   storage = atapi.AnnotationStorage(migrate=True),
                   widget = MultiFileWidget(
                           description = "",
                           label= "Fichier(s)",
                           show_content_type = False,)
        ),


))

schemata.finalizeATCTSchema(ArticleSchema)


class BurocomArticle(document.ATDocument):
    """BurocomArticle type"""
    implements(IBurocomArticle)

    schema = ArticleSchema
    meta_type = "BurocomArticle"
    
    security = ClassSecurityInfo()

    # Copied from ATCT and adapted to work w/ the 3 images.
    # See later if this is not provided in a generic and better way by
    # plone.app.imaging.
    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = None
            if name.startswith('image1'):
                field = self.getField('image1')
            elif name.startswith('image2'):
                field = self.getField('image2')
            else:
                field = self.getField('image')
            image = None
            if name in ['image', 'image1', 'image2']:
                image = field.getScale(self)
            else:
                scalename = ''
                if name.startswith('image1'):
                    scalename = name[len('image1_'):]
                elif name.startswith('image2'):
                    scalename = name[len('image2_'):]
                else:
                    scalename = name[len('image_'):]
                    
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return document.ATDocument.__bobo_traverse__(self, REQUEST, name)
        

atapi.registerType(BurocomArticle, PROJECTNAME)
