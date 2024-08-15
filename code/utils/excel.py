import os

import pandas as pd

report_fname = "QE_scores.xlsx"  # name and path specified in config


def create_xls_report(bitexts, source_lang, target_lang, omtprj_dpath):
    omtproj_dname = os.path.basename(omtprj_dpath)
    print(f"{omtproj_dname=}")

    df = pd.DataFrame(bitexts)

    mtpe_dir = os.path.join(omtprj_dpath, "mtpe")
    os.makedirs(mtpe_dir, exist_ok=True)

    # Save the DataFrame to an Excel file
    df.to_excel(
        os.path.join(mtpe_dir, report_fname), index=False, sheet_name=target_lang
    )

    # print(f"{reports_dpath=}")
    df.to_excel(f"{omtproj_dname}_{report_fname}", index=False, sheet_name=target_lang)

    print("Data has been saved to 'report_fname'")


# bitexts = [
#     {
#         "src": "Develop reasoning frameworks",
#         "mt": "Développer des cadres de raisonnement",
#         "score": 0.862553596496582,
#     },
#     {
#         "src": "Accuracy aims to improve the precision and correctness in one's analysis and decision-making processes.",
#         "mt": "L'exactitude vise à améliorer la précision et l'exactitude des processus d'analyse et de prise de décision.",
#         "score": 0.8695585131645203,
#     },
#     {
#         "src": "Developing reasoning frameworks is crucial for enhancing accuracy and making sound decisions.",
#         "mt": "Développer des cadres de raisonnement est essentiel pour améliorer la précision et prendre des décisions judicieuses.",
#         "score": 0.8910650014877319,
#     },
# ]
