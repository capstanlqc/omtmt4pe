import os
import math
import numpy as np
from dotenv import load_dotenv
from modernmt import ModernMT

# arguments: mt provider, projects path

load_dotenv()
MODERNMT_API_KEY = os.environ["MODERNMT_API_KEY"]

mmt = ModernMT(MODERNMT_API_KEY, "omtmt4pe", "1.2.8")

def get_mmt_translations(source_lang, target_lang, segments):

    number_of_segments = len(segments)
    if number_of_segments > 128:
        #logging.info("Too many segments, it's necessary to split to avoid 'google.api_core.exceptions.BadRequest'.")
        #logging.info("Let's limit the number of segments per batch to 100")
        num_of_batches = math.ceil(number_of_segments / 128)
        batches = np.array_split(segments, num_of_batches)
    else:
        batches = np.array_split(segments, 1)

    translations = []
    usage = 0
    for array in batches:
        segments_in_batch = list(array)
        
        # batch_xlats = [html.unescape(x["translatedText"]) 
        #    for x in translate_client.translate(segments_in_batch, target_language=target_langtag)]
        
        output = mmt.translate(source_lang, target_lang, segments_in_batch)
        batch_xlats = [unit.translation for unit in output]
        usage += sum(unit.billedCharacters for unit in output)
        translations.extend(batch_xlats)

    bitexts = dict(zip(segments, translations))
    return bitexts, usage    