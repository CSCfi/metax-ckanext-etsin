from iso639 import languages


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


def get_language_identifier(lang):
    if not isinstance(lang, basestring):
        lang = 'und'

    return 'http://lexvo.org/id/iso639-3/' + lang
