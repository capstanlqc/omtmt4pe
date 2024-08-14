import argparse
import sys

from mt.deepl import get_deepl_translations
from mt.google import get_google_langtags, get_google_translations
from mt.modernmt import get_mmt_translations
from utils.omegat import get_segments
from utils.tmx import compose_tmx, save_tmx_file

# run as:
# python code/main.py -e ModernMT -c no-confi-for-now -p $omtproj_dpath

text = "This program: \
(1) extracts source text (segments) from omegat project, \
(2) translates the project, \
(3) adds a TM with the results to the project. "

# intialize arg parser with a description
parser = argparse.ArgumentParser(description=text)
parser.add_argument("-V", "--version", help="show program version", action="store_true")
parser.add_argument(
    "-c",
    "--config",
    help="specify path to config file, by default at ./config/config.ods",
)
parser.add_argument(
    "-p",
    "--project",
    help="specify path to folder containing the OmegaT project and the monitoring form",
)
parser.add_argument(
    "-e",
    "--engine",
    help="specify the survey name that will be used to name other things",
)

# read arguments from the command line
args = parser.parse_args()

# check for -V or --version
if args.version:
    print("This is OMTMT4PE utility version 0.1.0")
    sys.exit()

if args.project and args.config and args.engine:
    print("Config: Using preferences from %s" % args.config)
    print(f"MT: Using MT provider {args.engine}")
    omtprj_dpath = args.project.rstrip("/")
    config_fpath = args.config.rstrip("/")
    mt_engine = args.engine.strip()
else:
    print("Arguments -s, -c and -p not found.")
    sys.exit()


# MODERNMT_API_KEY = os.environ["MODERNMT_API_KEY"]

# todo:
# check if tm is already created
# check config: option overwrite

# get segments
source_lang, target_lang, segments = get_segments(omtprj_dpath)
# todo: get_props ...

match mt_engine.lower():
    case "modernmt" | "modern" | "mmt":
        # check whether engine supports language pair
        # languages = mmt.list_supported_languages()
        bitexts, usage = get_mmt_translations(source_lang, target_lang, segments)
    case "deepl":
        bitexts, usage = get_deepl_translations(source_lang, target_lang, segments)
    case "google" | "google translate" | "google mt":
        google_langtags = get_google_langtags()
        bitexts, usage = get_google_translations(target_lang, segments)
    case _:
        print("LLLM????  commmet??")

# sys.exit()
# todo: post usage to mt-usage

try:
    if usage > 0:
        info = {
            "source_lang": source_lang,
            "target_lang": target_lang,
            "creationtool": "omtpt4pe",
        }
        print(f"{info}")
        tmx_str = compose_tmx(info, bitexts)
        save_tmx_file(tmx_str, omtprj_dpath, mt_engine.lower())

except NameError:
    print("Variable 'usage' is not defined")

# ask kos to add logging, type hints, docstrings, try/except blocks
