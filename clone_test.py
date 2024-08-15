import os
from dotenv import load_dotenv

# ############# PROGRAM DESCRIPTION ###########################################

# load environment variables
load_dotenv()

files_dpath = os.environ["files_dpath"]

url = "https://github.com/capstanlqc-test/TEST_ara-ZZZ_OMT.git"

clone_command = f"git clone --depth 1 {url} {proj_dpath}"

os.system(clone_command)

# clone team project to offline copy
