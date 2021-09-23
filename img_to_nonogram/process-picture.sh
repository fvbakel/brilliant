
fullfile=$1
python3 img_to_nonogram.py -f $@

data_dir=`dirname $fullfile`
filename=$(basename -- "$fullfile")
filename="${filename%.*}"

puzzle=`ls ${data_dir}/${filename}*.txt`

/opt/bin/nonogram ${puzzle}
