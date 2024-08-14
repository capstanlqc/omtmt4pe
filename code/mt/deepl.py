import json
import logging
import os

import deepl
import requests
from dotenv import load_dotenv

load_dotenv()
DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]


def get_transl(segm_list, source_lang, target_lang):
    if DEEPL_API_KEY is None:
        print("ERROR: No API key, use another engine")
        # some_fallback_operation(  )
    else:
        # get the translations
        response = requests.post(
            url="https://api.deepl.com/v2/translate",
            data={
                "source_lang": source_lang,
                "target_lang": target_lang,
                "auth_key": DEEPL_API_KEY,
                "text": segm_list,
            },
        )

        if response.status_code == 200:
            data = json.loads(response.text)
            translations = data["translations"]
            # for xlat in translations: # type list
            #     print(xlat['text'])
            return [xlat["text"] for xlat in translations]
        else:
            print(
                "ERROR: The connection didn't resolve successfully, perhaps some data (language subtags) is wrong."
            )
            return None


def define_deepl_translator(DEEPL_API_KEY):
    """Defines translator object"""

    if DEEPL_API_KEY is None:
        print("ERROR: No API key, the translator object will not be created")
        # some_fallback_operation(  )
        return None
    else:
        print("INFO: API key is defined")  #: {api_key}")
        # Create a Translator object providing your DeepL API authentication key
        translator = deepl.Translator(DEEPL_API_KEY)
        return translator


def get_deepl_langtags(translator):
    """Get DeepL supported language codes"""
    # Source and target languages

    try:
        logging.debug("Trying to get the lists of language tags supported by DeepL")
        deepl_source_langtags = [
            language.code.lower() for language in translator.get_source_languages()
        ]
        deepl_target_langtags = [
            language.code.lower() for language in translator.get_target_languages()
        ]
        logging.debug(
            f"{'source:', deepl_source_langtags, 'target:', deepl_target_langtags}"
        )
    except Exception as err:
        print(f"ERROR: {err=}")

    if not deepl_source_langtags or not deepl_target_langtags:
        return None

    return {"source": deepl_source_langtags, "target": deepl_target_langtags}


def source_lang_is_supported(source_lang, deepl_langtags):
    """Checks whether DeepL can translate from the source language"""
    print(f"{source_lang=}")
    src_lang_subtag = source_lang.split("-")[0]
    print(f"{src_lang_subtag=}")
    print(f"INFO: {src_lang_subtag=}")
    if src_lang_subtag in deepl_langtags["source"]:
        return True
    else:
        return False


def get_current_usage(translator):
    usage = translator.get_usage()
    if usage.any_limit_reached:
        print("Translation limit reached.")
    elif usage.character.valid:
        print(f"Character usage: {usage.character.count} of {usage.character.limit}")
        return usage.character.count
    # if usage.document.valid:
    #    print(f"Document usage: {usage.document.count} of {usage.document.limit}")


def get_deepl_translations(source_lang, target_lang, segm_list):
    """Uses python client instead of the API directly"""

    if target_lang == "pt":
        target_lang = "pt-PT"

    print(f"INFO: Translate from {source_lang=} into {target_lang=}")
    print(f"Translate from {source_lang=} into {target_lang=}")

    translator = define_deepl_translator(DEEPL_API_KEY)

    usage_before = get_current_usage(define_deepl_translator(DEEPL_API_KEY))

    if translator == None:
        print("deepl translator is none")
        return None

    deepl_langtags = get_deepl_langtags(translator)

    if not source_lang_is_supported(source_lang, deepl_langtags):
        logging.warning(f"DeepL does not support language {source_lang}")
        print(f"DeepL does not support language {source_lang}")
        return None

    translations = [
        x.text for x in translator.translate_text(segm_list, target_lang=target_lang)
    ]

    usage_after = get_current_usage(define_deepl_translator(DEEPL_API_KEY))
    print(f"{usage_before=}")
    print(f"{usage_after=}")
    # for some reason the usage_after is identical to usage_before (within the same session)

    total_char_count = sum([len(string) for string in segm_list])

    return (dict(zip(segm_list, translations)), total_char_count)
