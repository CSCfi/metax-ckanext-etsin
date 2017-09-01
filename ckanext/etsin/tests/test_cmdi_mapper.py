from ckanext.etsin.mappers.cmdi import cmdi_mapper
import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
from .helpers import _get_file_as_string


class TestCmdiMapper(TestCase):
    source = {}
    source['xml'] = _get_file_as_string(
        'kielipankki_cmdi/cmdi_record_example.xml')
    data_dict = {'package_dict': {}}
    metax_dict = cmdi_mapper(source, data_dict)['metax_dict']

    # TODO: validate fields (or at least check existence)
    # Right now we're basically just checking that it does
    # not throw an error with the input

    # Test preferred identifier
    # Note that the identifier will be assigned by refiner, not mapper
    def testPreferredIdentifier(self):
        assert 'preferred_identifier' in self.metax_dict['research_dataset']

    # Test language
    def testLanguage(self):
        import pprint
        pprint.pprint(self.metax_dict)
        assert {
            'identifier': 'http://lexvo.org/id/iso639-3/fin',
            'title': u'fi',
        } in self.metax_dict['research_dataset']['language']

    # Test title

    # Test creators

    def testCreatorPerson(self):
        assert {
            'email': 'teija@tekija.fi',
            'name': u'Teija Tekij\xe4',
            'phone': '+358501234567',
            'isPartOf': {'email': 'registry@utu.fi',
                         'name': u'University of Turku',
                         'phone': '',
                         }
        } in self.metax_dict['research_dataset']['creator']

    def testCreatorOrganization(self):
        assert {
            'email': 'etunim.sukunimi@kotus.fi',
            'name': u'Kotimaisten kielten keskus, Institute for the Languages of Finland',
            'phone': '+358 295 333 200',
        } in self.metax_dict['research_dataset']['creator']

    # Test curators

    def testCuratorPerson1(self):
        assert {
            'email': 'nobufumi.inaba@utu.fi',
            'isPartOf': {'email': 'registry@utu.fi',
                         'name': u'University of Turku',
                         'phone': ''},
            'name': u'Nobufumi Inaba',
            'phone': '+358 123 456 789',
        } in self.metax_dict['research_dataset']['curator']

    def testCuratorPerson2(self):
        assert {
            'email': 'kaisa.hakkinen@utu.fi',
            'isPartOf': {'email': 'registry@utu.fi',
                         'name': u'University of Turku',
                         'phone': ''},
            'name': u'Kaisa H\xe4kkinen',
            'phone': '',
        } in self.metax_dict['research_dataset']['curator']

    def testCuratorOrganization1(self):
        assert {
            'email': 'etunim.sukunimi@kotus.fi',
            'name': u'Kotimaisten kielten keskus, Institute for the Languages of Finland',
            'phone': '+358 295 333 200',
        } in self.metax_dict['research_dataset']['curator']

    def testCuratorOrganization2(self):
        assert {
            'email': 'registry@utu.fi',
            'name': u'University of Turku',
            'phone': '',
        } in self.metax_dict['research_dataset']['curator']


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
