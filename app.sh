#!/usr/bin/env bash

# todo check whether app_root is relative to the script or from where it is run
app_root=$(pwd)

# load environment variables
# export $(grep -v '^#' .env | xargs)
set -a && source $app_root/.env && set +a

# read locales and engines from config.json
locales=(es fr pt ro de pl)
engine="mmt"
# todo: read mt providers from config

# if input is template: create omegat projects
for tmpl_omtpkg_fpath in $(find $tmpl_dpath -maxdepth 1 -type f -name "*.omt")
do
    for locale in "${locales[@]}"
    do
        echo "======= $locale ======="
        tmpl_omtprj_dname=$(basename $tmpl_omtpkg_fpath .omt)
        omtprj_dname="${tmpl_omtprj_dname/xx/"$locale"}"
        echo "omtprj_dname: $omtprj_dname"
        omtprj_dpath=$files_dpath/$omtprj_dname
        # find $files_dpath -name $omtprj_dname -exec rm -r $omtprj_dpath {} +
        [ -d $omtprj_dpath ] && rm -r $omtprj_dpath
        yes | unzip -d $omtprj_dpath $tmpl_omtpkg_fpath > /dev/null 2>&1
        perl -i -pe "s/(?<=<target_lang>)xx/$locale/" $omtprj_dpath/omegat.project
    done
done

for omtprj_dpath in $(find $files_dpath -maxdepth 1 -type d)
do

    cd $app_root

    [ -f $omtprj_dpath/omegat.project ] || continue
    echo $omtprj_dpath

    mkdir -p $omtprj_dpath/tm/auto/mt
    find "$omtprj_dpath/tm/auto/mt" -name "*.tmx" -exec rm {} +
    
    $jrebin_fpath -jar $omegat_jpath \
        $omtprj_dpath \
        --mode=console-translate \
        --config-dir=$config_dpath \
        --script=$script_fpath  > /dev/null 2>&1

    echo "python code/main.py -e $engine -c no-confi-for-now -p $omtprj_dpath"
    python code/main.py -e $engine -c no-confi-for-now -p $omtprj_dpath

    cd $omtprj_dpath
    omtprj_dname=$(basename $omtprj_dpath)
    mkdir -p $app_root/files/output/$engine
    output_omtpkg_fpath="$app_root/files/output/$engine/${omtprj_dname}.omt"
    zip -r $output_omtpkg_fpath * > /dev/null 2>&1
    echo "MT'ed package saved at $output_omtpkg_fpath"
    find "$omtprj_dpath/tm/auto/mt" -name "*.tmx" -exec rm {} +

    # cd $app_root
    echo "-----"
done



# register usage to mt_usage api


# if source files are provided, create projects on the fly