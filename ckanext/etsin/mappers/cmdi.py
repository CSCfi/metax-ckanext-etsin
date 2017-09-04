'''
Map CMDI based dicts to Metax values
'''
from ckanext.etsin.cmdi_parse_helper import CmdiParseHelper

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

        languages = cmdi.parse_languages()
        language_list = [{'title': lang, 'identifier': 'todo'}
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

        creators = cmdi.parse_creators()
        distributor = cmdi.parse_distributor()
        owners = cmdi.parse_owners()
        curators = cmdi.parse_curators()

        metax_dict = {
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "contract": "1",
            # TODO: "etsin" or such (doesn't exist yet in metax)
            "dataset_catalog": "1",
            "research_dataset": {
                "creator": creators,
                "distributor": distributor,
                "modified": modified,
                "title": title_list,
                "files": ["todo"],
                "curator": curators,
                "ready_status": "todo",
                "urn_identifier": "todo",
                "total_byte_size": 0,
                "description": description_list,
                "version_notes": ["todo"],
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

        return metax_dict


def cmdi_mapper(context, data_dict):
    """ Maps a CMDI record in xml format into a MetaX format dict. """

    package_dict = data_dict['package_dict']
    xml = context.pop('xml')
    metax_dict = CmdiMetaxMapper.map(xml)
    package_dict.update(metax_dict)
    return package_dict