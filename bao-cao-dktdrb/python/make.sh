set -e
W=$(dirname $0); OUT=$1; NAME=$2; LOGO=$3
python3 $W/build_doc.py $OUT/$NAME.docx /nonexistent $LOGO
soffice --headless --convert-to pdf --outdir $OUT $OUT/$NAME.docx >/dev/null 2>&1
python3 $W/pages.py $OUT/$NAME.pdf $OUT/$NAME.docx.meta.json $OUT/pages.json
python3 $W/build_doc.py $OUT/$NAME.docx $OUT/pages.json $LOGO
soffice --headless --convert-to pdf --outdir $OUT $OUT/$NAME.docx >/dev/null 2>&1
python3 $W/pages.py $OUT/$NAME.pdf $OUT/$NAME.docx.meta.json $OUT/pages2.json
cmp <(python3 -c "import json;print(sorted(json.load(open('$OUT/pages.json')).items()))") <(python3 -c "import json;print(sorted(json.load(open('$OUT/pages2.json')).items()))") && echo PAGES_STABLE
