# OMTMT4PE

This app's name stands for something like "machine translation for post-editing in OmegaT".

This is a service that runs in Ur for internal consumption of the cApStAn team. This is a proof of concept, and a web service can be created to allow partners to send requests to this service from outside Ur.

## Usage

The **files folder** where you must drop your input files is `/media/data/data/company/Apps/omtmt4pe` (probably mounted as `U:\Apps\omtmt4pe` on a Windows machine). 

> Any other folder can be used if it's more convenient for you, just let us know.

Your input is different depending on what you'd like to machine-translate:

- Offline project packages
- Online team projects

The output, in any case, will be a TM containing MT translations, added to the project under `tm/auto/mt` (or the path provided in the configuration as the value of key `destination-for-mt-tm`).

The TM containing the translation from DeepL is in `tm/auto/mt/deepl_YYYYMMDD.tmx`.

### Project packages

Drop your OMT package(s) in the **files folder**.

Each project will be machine-translated and moved to `/media/data/data/company/Apps/omtmt4pe/done`, ready to be dispatched to the post-editor.

### Team projects

Drop your a `repos.txt` file in **files folder** containing one line for each repo url, e.g. 

    https://github.com/capstanlqc-test/TEST_bul-BGR_OMT.git
    https://github.com/capstanlqc-test/TEST_ara-ZZZ_OMT.git

Each team project will be machine-translated online. The MT translations will be visible when the user downloads the project in OmegaT.

## Configuration

1. Tweak configuration file `config.json` as suitable.
2. Put it in the **files folder** or inside the `omegat` folder of the project before you drop your files.

Options:

- **`keep-existing-translations`** (false by default): Depending on whether this key is set to `true` or `false`, the output TM containing MT translations will include existing translations from the working TM. 
- **`destination-for-mt-tm`** (`tm/auto/mt` by default): The TM containing MT translations will be added in this location of the project before re-packing it or committing the file.

## TODO (dev info)

- Log some stats: project, wordcount, language pair, engine, expense, etc. 
- Segments for which there is a translation should not be sent to the MT engine if `keep-existing-translations` is set to `true`
- Fine tune the script to translate only segments that don't have a translation coming from...
	* project_save.tmx?
	* tm/auto*?
	* tm/enforce*?
	* etc.
- API-based web service for other partners or platforms to request MT for an OmegaT project (WIP) 
- Add Google Translate, etc. for languages that DeepL does not support (in a list, from higher to lower preference)
- Add quality estimation (WIP)
- Use `destination-for-mt-tm` value (instead of hard-coded `tm/auto/mt`)
- Read config file `mt_config.json` or `mt_config.xlsx` from `project_root/omegat` (if found, ignore the one in the files folder)
- Add user options to config, e.g. user options (form of address, etc.)
- Tweak the groovy script to include such options, glossaries, etc.

## Deployment (dev info)

A `.env` file in the app root must contain valid paths to all parameters. Copy `.env-ur` to `.env` for convenience.

Script `/path/to/run.sh` is scheduled to run every minute.


--- 

### TODO:

- put config.json inside omegat package(s), or next to it in template, or in omtpkgs
if found inside the project, it takes precedence over the one found next to packages


-- DIferent ways to run the thing:
- from an XX omegat project template -> instances for all languages specified in config
- from one or more omegat project packages (instances)
- frmo a team project template (todo?)
- from a list of git-hosted team projects (repos.txt)

-> 
create offline projects (folders) that omegat can interact with

-> output: 
- if packages -> output packages moved to done
- if team projects -> commit files and add url to done/repos.txt

config:

- modules: 
-- mt: providers
-- qe: true, models...

TIps.

add region subtag
(for mt it's easier to remove it than to add it)
- 