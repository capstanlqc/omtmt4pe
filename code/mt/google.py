# https://cloud.google.com/docs/authentication/getting-started
# https://github.com/googleapis/python-translate/blob/HEAD/samples/snippets/snippets.py

import html
import math
import os

import numpy as np
from dotenv import load_dotenv

# pipenv install google-cloud-translate
from google.cloud import translate_v2 as translate

load_dotenv()
credential_fpath = (
    "/run/media/souto/257-FLASH/nlp_dev/config/capps-translation-api-1bd7868e82db.json"
)
# credential_fpath = "/home/souto/Sync/Dev/python_tests/capps-translation-api-1bd7868e82db.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_fpath


def get_google_langtags():
    """Lists all available languages."""  # unlike with the previous API, it seems the same languages are supported as both source and target

    translate_client = translate.Client()

    return [lang["language"] for lang in translate_client.get_languages()]


def get_google_translations(target_langtag, list_of_strings):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages


    There seems to be a limit of 128 in the number of segments the API can process in one single batch.
    Exceeding that limit results in error 'google.api_core.exceptions.BadRequest: 400 POST https://translation.googleapis.com/language/translate/v2?prettyPrint=false: Too many text segment'
    To avoid that, the list of strings is split in batches of 100 segments, and posted individually, and merged afterwards.
    """

    translate_client = translate.Client()

    # if isinstance(list_of_strings, six.binary_type):
    #    list_of_strings = list_of_strings.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    # result = translate_client.translate(text, target_language=target)
    # print(u"Text: {}".format(result["input"]))
    # print(u"Translation: {}".format(result["translatedText"]))
    # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))

    total_char_count = sum([len(string) for string in list_of_strings])

    number_of_segments = len(list_of_strings)
    if number_of_segments > 100:
        # logging.info("Too many segments, it's necessary to split to avoid 'google.api_core.exceptions.BadRequest'.")
        # logging.info("Let's limit the number of segments per batch to 100")
        num_of_batches = math.ceil(number_of_segments / 100)
        batches = np.array_split(list_of_strings, num_of_batches)
    else:
        batches = np.array_split(list_of_strings, 1)

    translations = []
    for array in batches:
        list_of_strings_in_batch = list(array)
        batch_xlats = [
            html.unescape(x["translatedText"])
            for x in translate_client.translate(
                list_of_strings_in_batch, target_language=target_langtag
            )
        ]
        translations.extend(batch_xlats)

    # usage = sum(unit.billedCharacters for unit in output)
    # bitexts = dict(zip(list_of_strings, translations))

    bitexts = dict(zip(list_of_strings, translations))
    return bitexts, total_char_count
