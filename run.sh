#!/usr/bin/env bash

# load environment variables
# export $(grep -v '^#' .env | xargs)
set -a && source $app_root/.env && set +a

app_root=$(pwd)
mkdir -p $files_dpath/done

# functions
get_config() {
    echo "config_fpath=$files_dpath/config.json"
    config_fpath=$files_dpath/config.json
    if [ -f $config_fpath ]
    then
        keep_existing_translations=$(jq -r '.["keep-existing-translations"]' "$config_fpath")
    fi
}

get_repo_name() {
    local url="$1"
    # Remove .git suffix and get the last part after /
    echo "$(basename -s .git $url)"
}

unempty_folder() {
    local dpath="$1"
    find $dpath -empty -type d -exec touch {}/.gitkeep \; # function
}

fetch_mapped_files() {
    local omtprj_dpath="$1"

    echo "Fetch mapped files for $omtprj_dpath"
    echo "mkdir -p $omtprj_dpath/.repos/"
    mkdir -p $omtprj_dpath/.repos/

    # nodes="$(xmlstarlet select -t -v "//repository[@type='git']/@url" $omtprj_dpath/omegat.project)" 

    xmlstarlet sel -t \
        -m "//mapping" \
        -v "concat(@local, '|', @repository, '|', ../@url)" \
        -n $omtprj_dpath/omegat.project | \
    while IFS="|" read -r local repository url; do
        
        [ "$local" == "/" ] && continue
        
        echo "-------------"
        echo "local: $local, repository: $repository, url: $url"
        repo_dpath=$(get_repo_name "$url")
        echo "repo_dpath: $repo_dpath"
        
        echo "git clone $url $omtprj_dpath/.repos/$repo_dpath"
        [ -d $omtprj_dpath/.repos/$repo_dpath ] || git clone $url $omtprj_dpath/.repos/$repo_dpath
        
        echo "[ -d $omtprj_dpath/.repos/$repo_dpath/$repository ] && mkdir -p $omtprj_dpath/$local"
        [ -d "$omtprj_dpath/.repos/$repo_dpath/$repository" ] && mkdir -p "$omtprj_dpath/$local"

        echo "rsync -a $omtprj_dpath/.repos/$repo_dpath/$repository $omtprj_dpath/$local"
        rsync -a "$omtprj_dpath/.repos/$repo_dpath/$repository" "$omtprj_dpath/$local"
    done
    
    # xmlstarlet select -t -c "//mapping[contains(@local, 'source')]" $omtprj_dpath/omegat.project #   | grep -Poh '(?<=local="source/)[^"]+'
    echo ""    
}

# archive done omt projects
for file_path in $(find $files_dpath -maxdepth 1 -type f -name "*");
do
    file_name="${file_path##*/}"
    # stem_path="${file_path%.omt}"
    stem_name="${file_name%.*}"

    report_fpath="$files_dpath/done/${stem_name}_LQA.xlsx"
    [[ -f $report_fpath ]] && mv $file_path $files_dpath/done
done

# run omegat+script on omt files
for omtpkg_fpath in $(find $files_dpath -maxdepth 1 -type f -name "*.omt")
do
	# unpack project
	omtpkg_fname="${omtpkg_fpath##*/}"
	omtprj_dname="${omtpkg_fname%.omt}"
	omtprj_dpath="${files_dpath}/${omtprj_dname}"
	yes | unzip -d $omtprj_dpath $omtpkg_fpath
    unempty_folder $omtprj_dpath

	# mt
	$jrebin_fpath -jar $omegat_jpath $omtprj_dpath --mode=console-translate --config-dir=$config_dpath  --script=$script_fpath

	# re-pack
	sleep 5
	find $omtprj_dpath/tm/auto/mt -name "deepl_*.tmx.bak" -exec rm {} \;
	rm $omtprj_dpath/$omtprj_dname-*.tmx
	cd $omtprj_dpath && zip -r $files_dpath/done/$omtpkg_fname *

	# clean up
	# cd $files_dpath
	[[ -f $files_dpath/done/$omtpkg_fname ]] && echo yes | rm -r $omtpkg_fpath $omtprj_dpath
done

# run omegat+script on team projects
[[ -f $files_dpath/repos.txt ]] && for repo in $(cat $files_dpath/repos.txt)
do
    omtprj_dpath=$(get_repo_name "$repo")
    echo "==================== $omtprj_dpath ===================="
    git clone --depth 1 $repo $files_dpath/$omtprj_dpath

    unempty_folder $files_dpath/$omtprj_dpath
    fetch_mapped_files $files_dpath/$omtprj_dpath
    mkdir -p $app_root/offline
    echo "cp -r $files_dpath/$omtprj_dpath $app_root/offline/${omtprj_dpath}_OMT"
    cp -r $files_dpath/$omtprj_dpath $app_root/offline/${omtprj_dpath}_OMT

    echo "xmlstarlet ed -d //repositories $app_root/offline/${omtprj_dpath}_OMT/omegat.project"
    xmlstarlet ed --inplace -d "//repositories" $app_root/offline/${omtprj_dpath}_OMT/omegat.project

    get_config
    echo "keep_existing_translations: $keep_existing_translations"
    [[ "$keep_existing_translations" == "false" ]]; mv $app_root/offline/${omtprj_dpath}_OMT/omegat/project_save.tmx $app_root/offline/${omtprj_dpath}_OMT/omegat/project_save.tmx.BAK-NOW

    echo "mt"
    $jrebin_fpath -jar $omegat_jpath $app_root/offline/${omtprj_dpath}_OMT --mode=console-translate --config-dir=$config_dpath  --script=$script_fpath

    echo "word counts"
    remaining=$(jq -r '.["remaining"]["characters"]' $app_root/offline/${omtprj_dpath}_OMT/omegat/project_stats.json)
    echo "send remaining, project, languages, date, etc. to the mt-usage API"

    sleep 5
	find $app_root/offline/${omtprj_dpath}_OMT/tm/auto/mt -name "deepl_*.tmx.bak" -exec rm {} \;

    echo "push TM to repo"
    echo "mkdir -p $files_dpath/$omtprj_dpath/tm/auto/mt"
    mkdir -p $files_dpath/$omtprj_dpath/tm/auto/mt
    echo "find $app_root/offline/${omtprj_dpath}_OMT/tm/auto/mt -name deepl_*.tmx -exec cp {} $files_dpath/$omtprj_dpath/tm/auto/mt \;"
    find $app_root/offline/${omtprj_dpath}_OMT/tm/auto/mt -name "deepl_*.tmx" -exec cp {} $files_dpath/$omtprj_dpath/tm/auto/mt \;

    cd $files_dpath/$omtprj_dpath
    git pull && git add $files_dpath/$omtprj_dpath/tm/auto/mt/* && git commit -m "Added MT TM"
    pushed=$(git push)
    cd -

    echo "if push went okay, remove url from Files/repos.txt and add ti Files/done/repos.txt"
    touch $files_dpath/done/repos.txt
    echo "echo $repo >> $files_dpath/done/repos.txt"
    echo $repo >> $files_dpath/done/repos.txt
    echo "sed -i \%$repo%d $files_dpath/done/repos.txt"
    sed -i "\%$repo%d" $files_dpath/repos.txt
    echo ""

    echo "clean up the mess"
    echo "find $files_dpath -type d -name $omtprj_dpath -exec rm -rf {} +"
    find $files_dpath -type d -name $omtprj_dpath -exec rm -rf {} +
    echo "find $app_root/offline -type d -name ${omtprj_dpath}_OMT -exec rm -rf {} +"
    find $app_root/offline -type d -name ${omtprj_dpath}_OMT -exec rm -rf {} +

done


