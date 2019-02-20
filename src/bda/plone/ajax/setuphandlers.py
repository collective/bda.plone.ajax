# -*- coding:utf-8 -*-
from Products.CMFPlone import interfaces as Plone
from zope.interface import implementer


@implementer(Plone.INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles.
        """
        return ['bda.plone.ajax:default']
