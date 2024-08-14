import os
from datetime import datetime

from lxml import etree


def compose_tmx(info, data):
    source_lang = info["source_lang"]
    target_lang = info["target_lang"]
    creationtool = info["creationtool"]

    # Create the root element
    root = etree.Element("tmx", version="1.4")

    # Add the header element
    header = etree.SubElement(
        root,
        "header",
        adminlang="en-us",
        creationtool=creationtool,
        creationtoolversion="1.0",
        segtype="sentence",
        srclang=source_lang,
        o_tmf="OmegaT",
    )

    # Add the body element
    body = etree.SubElement(root, "body")

    # Iterate over the dictionary and create translation units
    for source_text, target_text in data.items():
        tu = etree.SubElement(body, "tu")

        # Add source language segment
        # tuv_source = etree.SubElement(tu, 'tuv', {"xml:lang": source_lang})
        tuv_source = etree.SubElement(tu, "tuv")
        tuv_source.set("{http://www.w3.org/XML/1998/namespace}lang", source_lang)
        seg_source = etree.SubElement(tuv_source, "seg")
        seg_source.text = source_text

        # Add target language segment
        # tuv_target = etree.SubElement(tu, 'tuv', {"xml:lang": target_lang})
        tuv_target = etree.SubElement(tu, "tuv")
        tuv_target.set("{http://www.w3.org/XML/1998/namespace}lang", target_lang)
        seg_target = etree.SubElement(tuv_target, "seg")
        seg_target.text = target_text

    # Convert the XML to a string
    tmx_str = etree.tostring(
        root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )
    print("TMX composed")
    return tmx_str


def save_tmx_file(tmx_str, omtprj_dpath, engine):
    # Get today's date
    today = datetime.now()
    # Format date as YYYYMMDD
    timestamp = today.strftime("%Y%m%d")

    # Write to a TMX file
    output_mt_fname = f"{engine}_{timestamp}.tmx"
    output_mt_fpath = os.path.join(omtprj_dpath, "tm", "auto", "mt", output_mt_fname)

    # Ensure that the directories exist
    ancestor_dirs = os.path.dirname(output_mt_fpath)
    os.makedirs(ancestor_dirs, exist_ok=True)

    with open(output_mt_fpath, "wb") as f:
        f.write(tmx_str)

    print(f"TMX written to {output_mt_fpath}")
