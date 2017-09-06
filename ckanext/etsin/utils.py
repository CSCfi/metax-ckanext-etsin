from iso639 import languages
import json


def convert_language(language):
    '''
    Convert alpha2 language (eg. 'en') to terminology language (eg. 'eng')
    '''

    if not language:
        return "und"

    try:
        lang_object = languages.get(part1=language)
        return lang_object.terminology
    except KeyError as ke:
        try:
            lang_object = languages.get(part2b=language)
            return lang_object.terminology
        except KeyError as ke:
            return ''

def convert_language_to_6391(language):
    '''
    Convert ISO 639-2 and 639-3 language code ('fin') to ISO 639-1 ('fi'), if possible.
    Note that not all languages are included in ISO 639-1.
    '''
    return languages.get(part3=language).part1


def get_language_identifier(lang):
    '''
    Returns a URI representing the given ISO 639-3 encoded language
    '''
    if not isinstance(lang, basestring):
        lang = 'und'

    return 'http://lexvo.org/id/iso639-3/' + lang
  
def convert_to_metax_dict(data_dict, metax_id=None):
    '''
    :param data_dict: contains data that has come from harvester, mapped and refined
                        and about to be sent to metax
    :return: data_dict that conforms with metax json format
    '''

    import logging
    log = logging.getLogger(__name__)

    catalog_id = data_dict.pop('data_catalog')

    if metax_id:
        data_dict['urn_identifier'] =  metax_id
    try:
        # Do json dumps - loads routine to get rid of problematic character encodings
        return json.loads(json.dumps({'research_dataset': data_dict, 'data_catalog': catalog_id}, ensure_ascii=True))
    except Exception as e:
        log.error(e)
