'''
Map CMDI based dicts to Metax values
'''
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

from ..utils import get_language_identifier, convert_language

# For development use
import logging
log = logging.getLogger(__name__)

# Maps Component MetaData Infrastructure to Metax


class CmdiMetaxMapper:

    @staticmethod
    def map(xml):
        """ Convert given XML into MetaX format.
        :param xml: xml element (lxml)
        :return: dictionary
        """
        cmdi = CmdiParseHelper(xml)

        # Preferred identifier will be added in refinement
        preferred_identifier = None

        languages = cmdi.parse_languages()
        language_list = [{'title': lang,
                          'identifier': get_language_identifier(
                              convert_language(lang))}
                         for lang in languages]

        description_list = cmdi.parse_descriptions()
        title_list = cmdi.parse_titles()
        modified = cmdi.parse_modified() or ""

        temporal_coverage = cmdi.parse_temporal_coverage() or ""
        temporal_coverage_begin = ""
        temporal_coverage_end = ""
        if temporal_coverage:
            split = [item.strip() for item in temporal_coverage.split("-")]
            if len(split) == 2:
                temporal_coverage_begin = split[0]
                temporal_coverage_end = split[1]

        creators = cmdi.parse_creators()  # creators == owners
        owners = cmdi.parse_owners()  # implemented but not saved to dict
        distributor = cmdi.parse_distributor()
        curators = cmdi.parse_curators()

        return {
            "research_dataset": {
                "preferred_identifier": preferred_identifier,
                "creator": creators,
                "distributor": distributor,
                "modified": modified,
                "title": title_list,
                "curator": curators,
                "description": description_list,
                "language": language_list,
                "provenance": [{
                    "temporal": [{
                        "startDate": [
                            temporal_coverage_begin
                        ],
                        "endDate": [
                            temporal_coverage_end
                        ]
                    }]
                }]
            }
        }


def cmdi_mapper(xml):
    """ Maps a CMDI record in xml format into a MetaX format dict. """
    return CmdiMetaxMapper.map(xml)
