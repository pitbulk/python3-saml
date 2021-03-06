# -*- coding: utf-8 -*-

# Copyright (c) 2014, OneLogin, Inc.
# All rights reserved.

import json
from os.path import dirname, join, exists
import unittest

from onelogin.saml2 import compat
from onelogin.saml2.authn_request import OneLogin_Saml2_Authn_Request
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.xml_utils import OneLogin_Saml2_XML


try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs


class OneLogin_Saml2_Authn_Request_Test(unittest.TestCase):
    def loadSettingsJSON(self):
        filename = join(dirname(__file__), '..', '..', '..', 'settings', 'settings1.json')
        if exists(filename):
            stream = open(filename, 'r')
            settings = json.load(stream)
            stream.close()
            return settings
        else:
            raise Exception('Settings json file does not exist')

    def setUp(self):
        self.__settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

    def testCreateRequest(self):
        """
        Tests the OneLogin_Saml2_Authn_Request Constructor.
        The creation of a deflated SAML Request
        """

        saml_settings = self.loadSettingsJSON()
        settings = OneLogin_Saml2_Settings(saml_settings)
        settings._OneLogin_Saml2_Settings__organization = {
            u'en-US': {
                u'url': u'http://sp.example.com',
                u'name': u'sp_test'
            }
        }

        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertNotIn('ProviderName="SP test"', inflated)

        saml_settings['organization'] = {}
        settings = OneLogin_Saml2_Settings(saml_settings)

        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertNotIn('ProviderName="SP test"', inflated)

    def testCreateRequestAuthContext(self):
        """
        Tests the OneLogin_Saml2_Authn_Request Constructor.
        The creation of a deflated SAML Request with defined AuthContext
        """
        saml_settings = self.loadSettingsJSON()
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertIn(OneLogin_Saml2_Constants.AC_PASSWORD, inflated)
        self.assertNotIn(OneLogin_Saml2_Constants.AC_X509, inflated)

        saml_settings['security']['requestedAuthnContext'] = True
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertIn(OneLogin_Saml2_Constants.AC_PASSWORD_PROTECTED, inflated)
        self.assertNotIn(OneLogin_Saml2_Constants.AC_X509, inflated)

        del saml_settings['security']['requestedAuthnContext']
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertIn(OneLogin_Saml2_Constants.AC_PASSWORD_PROTECTED, inflated)
        self.assertNotIn(OneLogin_Saml2_Constants.AC_X509, inflated)

        saml_settings['security']['requestedAuthnContext'] = False
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertNotIn(OneLogin_Saml2_Constants.AC_PASSWORD_PROTECTED, inflated)
        self.assertNotIn(OneLogin_Saml2_Constants.AC_X509, inflated)

        saml_settings['security']['requestedAuthnContext'] = (OneLogin_Saml2_Constants.AC_PASSWORD_PROTECTED, OneLogin_Saml2_Constants.AC_X509)
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertIn(OneLogin_Saml2_Constants.AC_PASSWORD_PROTECTED, inflated)
        self.assertIn(OneLogin_Saml2_Constants.AC_X509, inflated)

    def testCreateRequestForceAuthN(self):
        """
        Tests the OneLogin_Saml2_Authn_Request Constructor.
        The creation of a deflated SAML Request with ForceAuthn="true"
        """
        saml_settings = self.loadSettingsJSON()
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertNotIn('ForceAuthn="true"', inflated)

        authn_request_2 = OneLogin_Saml2_Authn_Request(settings, False, False)
        authn_request_encoded_2 = authn_request_2.get_request()
        inflated_2 = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded_2))
        self.assertRegexpMatches(inflated_2, '^<samlp:AuthnRequest')
        self.assertNotIn('ForceAuthn="true"', inflated_2)

        authn_request_3 = OneLogin_Saml2_Authn_Request(settings, True, False)
        authn_request_encoded_3 = authn_request_3.get_request()
        inflated_3 = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded_3))
        self.assertRegexpMatches(inflated_3, '^<samlp:AuthnRequest')
        self.assertIn('ForceAuthn="true"', inflated_3)

    def testCreateRequestIsPassive(self):
        """
        Tests the OneLogin_Saml2_Authn_Request Constructor.
        The creation of a deflated SAML Request with IsPassive="true"
        """
        saml_settings = self.loadSettingsJSON()
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertNotIn('IsPassive="true"', inflated)

        authn_request_2 = OneLogin_Saml2_Authn_Request(settings, False, False)
        authn_request_encoded_2 = authn_request_2.get_request()
        inflated_2 = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded_2))
        self.assertRegexpMatches(inflated_2, '^<samlp:AuthnRequest')
        self.assertNotIn('IsPassive="true"', inflated_2)

        authn_request_3 = OneLogin_Saml2_Authn_Request(settings, False, True)
        authn_request_encoded_3 = authn_request_3.get_request()
        inflated_3 = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded_3))
        self.assertRegexpMatches(inflated_3, '^<samlp:AuthnRequest')
        self.assertIn('IsPassive="true"', inflated_3)

    def testCreateDeflatedSAMLRequestURLParameter(self):
        """
        Tests the OneLogin_Saml2_Authn_Request Constructor.
        The creation of a deflated SAML Request
        """
        authn_request = OneLogin_Saml2_Authn_Request(self.__settings)
        parameters = {
            'SAMLRequest': authn_request.get_request()
        }
        auth_url = OneLogin_Saml2_Utils.redirect('http://idp.example.com/SSOService.php', parameters, True)
        self.assertRegexpMatches(auth_url, '^http://idp\.example\.com\/SSOService\.php\?SAMLRequest=')
        exploded = urlparse(auth_url)
        exploded = parse_qs(exploded[4])
        payload = exploded['SAMLRequest'][0]
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(payload))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')

    def testCreateEncSAMLRequest(self):
        """
        Tests the OneLogin_Saml2_Authn_Request Constructor.
        The creation of a deflated SAML Request
        """
        settings = self.loadSettingsJSON()
        settings['organization'] = {
            'es': {
                'name': 'sp_prueba',
                'displayname': 'SP prueba',
                'url': 'http://sp.example.com'
            }
        }
        settings['security']['wantNameIdEncrypted'] = True
        settings = OneLogin_Saml2_Settings(settings)

        authn_request = OneLogin_Saml2_Authn_Request(settings)
        parameters = {
            'SAMLRequest': authn_request.get_request()
        }
        auth_url = OneLogin_Saml2_Utils.redirect('http://idp.example.com/SSOService.php', parameters, True)
        self.assertRegexpMatches(auth_url, '^http://idp\.example\.com\/SSOService\.php\?SAMLRequest=')
        exploded = urlparse(auth_url)
        exploded = parse_qs(exploded[4])
        payload = exploded['SAMLRequest'][0]
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(payload))
        self.assertRegexpMatches(inflated, '^<samlp:AuthnRequest')
        self.assertRegexpMatches(inflated, 'AssertionConsumerServiceURL="http://stuff.com/endpoints/endpoints/acs.php">')
        self.assertRegexpMatches(inflated, '<saml:Issuer>http://stuff.com/endpoints/metadata.php</saml:Issuer>')
        self.assertRegexpMatches(inflated, 'Format="urn:oasis:names:tc:SAML:2.0:nameid-format:encrypted"')
        self.assertRegexpMatches(inflated, 'ProviderName="SP prueba"')

    def testGetID(self):
        """
        Tests the get_id method of the OneLogin_Saml2_Authn_Request.
        """
        saml_settings = self.loadSettingsJSON()
        settings = OneLogin_Saml2_Settings(saml_settings)
        authn_request = OneLogin_Saml2_Authn_Request(settings)
        authn_request_encoded = authn_request.get_request()
        inflated = compat.to_string(OneLogin_Saml2_Utils.decode_base64_and_inflate(authn_request_encoded))
        document = OneLogin_Saml2_XML.to_etree(inflated)
        self.assertEqual(authn_request.get_id(), document.get('ID', None))
