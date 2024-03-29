# coding=UTF8
#
# This file is part of the Etsin harvester service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: GNU Affero General Public License version 3

from functionally import first

from ..metax_api import get_ref_data
from ..utils import get_tag_lang, get_string_as_valid_datetime_string

# For development use
import logging
log = logging.getLogger(__name__)


def ddi25_mapper(xml):
    """ Convert given DDI 2.5 XML into MetaX format dict.
    :param xml: xml element (lxml)
    :return: dictionary
    """

    namespaces = {'oai': "http://www.openarchives.org/OAI/2.0/",
                  'ddi': "ddi:codebook:2_5"}

    cb = first(xml.xpath('//oai:record/oai:metadata/ddi:codeBook', namespaces=namespaces))
    stdy = cb.find('ddi:stdyDscr', namespaces)

    # Preferred identifier
    pref_id = None
    id_nos = stdy.findall('ddi:citation/ddi:titlStmt/ddi:IDNo', namespaces)
    id_no = first(filter(lambda x: x.get('agency') == 'URN', id_nos))
    if id_no is not None:
        pref_id = id_no.text

    # Title
    title = {}
    titl = stdy.findall('ddi:citation/ddi:titlStmt/ddi:titl', namespaces)
    if len(titl):
        for t in titl:
            title[get_tag_lang(t)] = t.text

    # Creator
    # Assume that 'AuthEnty' tags for different language 'citations' are in same order
    creators = []
    try:
        for i, citation in enumerate(stdy.findall('ddi:citation', namespaces)):
            for j, author in enumerate(citation.xpath(
                    'ddi:rspStmt/ddi:AuthEnty|ddi:rspStmt/ddi:othId',
                    namespaces=namespaces)):
                agent_obj = {'name': None}
                if 'affiliation' in author.keys():
                    org = author.get('affiliation')
                    if i == 0:
                        agent_obj['@type'] = 'Person'
                        if org is not None:
                            agent_obj['member_of'] = {
                                'name': {
                                    get_tag_lang(author): org},
                                '@type': 'Organization'}
                        # TODO: Check here that othIds are handled correctly
                        agent_obj['name'] = author.text.strip()
                        creators.append(agent_obj)
                    elif org is not None:
                        creators[j]['member_of']['name'][get_tag_lang(author)] = org
                else:
                    if i == 0:
                        agent_obj['@type'] = 'Organization'
                        agent_obj['name'] = {get_tag_lang(author): author.text.strip()}
                        creators.append(agent_obj)
                    else:
                        creators[j]['name'][get_tag_lang(author)] = author.text.strip()
                if author.tag.split('}')[1] == 'othId':
                    log.info('Tag "othId" found, check it is correctly parsed(TODO)!')
    except Exception as e:
        log.error('Error parsing "creators": {0}: {1}. Check that different '
                  'language elements match at the source.'.format(e.__class__.__name__, e))
        raise

    # Modified
    modified = None
    ver_stmt = stdy.find('ddi:citation/ddi:verStmt/ddi:version', namespaces)
    if ver_stmt is not None and ver_stmt.get('date'):
        modified = get_string_as_valid_datetime_string(ver_stmt.get('date'), '01-01')

    # Description
    description = {}
    try:
        for abstract in stdy.findall('ddi:stdyInfo/ddi:abstract', namespaces):
            description[get_tag_lang(abstract)] = unicode(abstract.text).strip()
    except Exception as e:
        log.error('Error parsing "description": {0}: {1}'.format(e.__class__.__name__, e))
        raise

    # Keywords
    keywords = []
    for kw in stdy.findall('ddi:stdyInfo/ddi:subject/ddi:keyword', namespaces):
        keywords.append(kw.text.strip())
    vocab = 'CESSDA Topic Classification'
    for cterm in stdy.findall("ddi:stdyInfo/ddi:subject/ddi:topcClas[@vocab='{0}']".format(vocab), namespaces):
        keywords.append(cterm.text.strip())

    # Field of science
    codes = set()
    for fos in stdy.findall("ddi:stdyInfo/ddi:subject/ddi:topcClas[@vocab='OKM']", namespaces):
        field = 'label.' + get_tag_lang(fos)
        codes.add(get_ref_data('field_of_science', field, fos.text.strip(), 'code'))
    field_of_science = [{'identifier': c} for c in codes ]
    if not len(field_of_science):
        log.debug("No 'field of science' found.")
        field_of_science.append({'identifier': 'ta5'})

    # Publisher
    publisher = {
                    'name': {},
                    '@type': 'Organization',
                    "homepage": {
                        "title": {
                            "en": "Publisher website",
                            "fi": "Julkaisijan kotisivu"},
                        "identifier": ""}
    }
    for dist in stdy.findall('ddi:citation/ddi:distStmt', namespaces):
        distr = dist.find('ddi:distrbtr', namespaces)
        publisher['name'][get_tag_lang(distr)] = distr.text.strip()
        publisher['homepage']['identifier'] = distr.get('URI')

    # Temporal coverage
    tpath = "ddi:stdyInfo/ddi:sumDscr/ddi:{tag}[@event='{ev}']"
    tstart = stdy.find(tpath.format(tag='timePrd', ev='start'), namespaces) or\
        stdy.find(tpath.format(tag='collDate', ev='start'), namespaces)
    tend = stdy.find(tpath.format(tag='timePrd', ev='end'), namespaces) or\
        stdy.find(tpath.format(tag='collDate', ev='end'), namespaces)
    if tstart is None and tend is None:
        tstart = stdy.find(tpath.format(tag='timePrd', ev='single'), namespaces) or\
                 stdy.find(tpath.format(tag='collDate', ev='single'), namespaces)
        tend = tstart
    elif tstart is None or tend is None:
        log.error('No temporal coverage or only start or end date in dataset!')

    temporal_coverage_obj_1 = {}

    if tstart is not None and tstart.get('date'):
        start_dt = get_string_as_valid_datetime_string(tstart.get('date'), '01-01', '00:00:00')
        if start_dt is None:
            temporal_coverage_obj_1['temporal_coverage'] = tstart.get('date')
            if tend is not None and tend.get('date'):
                temporal_coverage_obj_1['temporal_coverage'] += ' - ' + tend.get('date')
        else:
            temporal_coverage_obj_1['start_date'] = start_dt
            if tend is not None and tend.get('date'):
                end_dt = get_string_as_valid_datetime_string(tend.get('date'), '12-31', '23:59:59')
                if end_dt is not None:
                    temporal_coverage_obj_1['end_date'] = end_dt

    # Provenance
    universe = {}
    univ = stdy.findall("ddi:stdyInfo/ddi:sumDscr/ddi:universe", namespaces)
    for u in univ:
        universe[get_tag_lang(u)] = u.text.strip()
    provenance = [{'title': {'en': 'Collection'},
                   'description': {
                       'en': 'Contains the date(s) when the data were collected.'},
                   'variable': [{'pref_label': universe}]
                   }]
    if temporal_coverage_obj_1:
        provenance[0]['temporal'] = temporal_coverage_obj_1

    # Production
    prod = stdy.find('ddi:citation/ddi:prodStmt/ddi:prodDate', namespaces)
    if prod is not None:
        temporal_coverage_obj_2 = {}

        if prod.text:
            start_dt = get_string_as_valid_datetime_string(prod.text.strip(), '01-01', '00:00:00')
            if start_dt is None:
                temporal_coverage_obj_2['temporal_coverage'] = prod.text.strip()
            else:
                temporal_coverage_obj_2['start_date'] = start_dt
                temporal_coverage_obj_2['end_date'] = get_string_as_valid_datetime_string(prod.text.strip(), '12-31',
                                                                                      '23:59:59')
        provenance.append(
            {'title': {'en': 'Production'},
             'description': {'en': 'Date when the data collection were'
                                   ' produced (not distributed or archived)'}})
        if temporal_coverage_obj_2:
            provenance[1]['temporal'] = temporal_coverage_obj_2

    # Geographical coverage
    spatial = [{}]
    lang_attr = '{http://www.w3.org/XML/1998/namespace}lang'
    lang_path = "ddi:stdyInfo/ddi:sumDscr/ddi:nation[@{la}='{lt}']"
    nat_fi = stdy.find(lang_path.format(la=lang_attr, lt='fi'), namespaces)
    nat_en = stdy.find(lang_path.format(la=lang_attr, lt='en'), namespaces)
    if nat_en is not None:
        spatial = [{'geographic_name': nat_en.text.strip()}]
    if nat_fi is not None:
        # Assume Finland so search ES for Finnish place names: 'nat_fi'
        spat_id = get_ref_data('location', 'label.fi', nat_fi.text.strip(),
                               'code')
        if spat_id is not None:
            spatial[0]['place_uri'] = {'identifier': spat_id}
        if spatial[0].get('geographic_name') is None:
            spatial[0]['geographic_name'] = nat_fi.text.strip()

    package_dict = {
        "preferred_identifier": pref_id,
        "title": title,
        "creator": creators,
        "description": description,
        "keyword": keywords,
        "field_of_science": field_of_science,
        "publisher": publisher,
        "provenance": provenance,
        "spatial": spatial
    }

    if modified is not None:
        package_dict['modified'] = modified

    if temporal_coverage_obj_1:
        package_dict['temporal'] = [temporal_coverage_obj_1]

    return package_dict
