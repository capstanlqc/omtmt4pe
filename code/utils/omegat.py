import os

from lxml import etree


def get_segments(omtprj_dpath):
    print(f"{omtprj_dpath=}")

    export_fpath = os.path.join(omtprj_dpath, "script_output", "allsource.txt")
    omtprj_fpath = os.path.join(omtprj_dpath, "omegat.project")

    # Load the XML file
    tree = etree.parse(omtprj_fpath)
    root = tree.getroot()

    # Use XPath to find the 'source_lang' element
    source_lang = root.xpath("//source_lang/text()")[0]
    target_lang = root.xpath("//target_lang/text()")[0]

    with open(export_fpath) as f:
        segments = [line.strip() for line in f.readlines() if line.strip()]

    return (source_lang, target_lang, segments)
