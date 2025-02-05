#!/bin/bash

destdir=$1
cwd=$(pwd)
dir=$(dirname ${cwd}/$(dirname $0))
[ "$destdir" = "" ] && destdir=$cwd

packagename=$(basename rpm/*.spec .spec)
version=$(head -n1 debian/changelog | cut -d'(' -f2 | cut -d')' -f1 | cut -d'-' -f1)
tmpdir=/tmp/${packagename}-${version}
echo $packagename
echo $version
echo $tmpdir


cd $dir
rm ${destdir}/${packagename}*.tar.gz  2>/dev/null || true
rm ${destdir}/${packagename}*.dsc     2>/dev/null || true
rm ${destdir}/${packagename}*.spec    2>/dev/null || true

cp rpm/${packagename}.spec /tmp/
cat /tmp/${packagename}.spec \
        | sed "s/^Version:.*/Version:        ${version}/" \
        | sed "s/^Source:.*/Source:         ${packagename}_${version}.tar.gz/" \
        | sed -ne '1,/%changelog/p' \
        > rpm/${packagename}.spec
rm /tmp/${packagename}.spec
cp rpm/${packagename}.spec $destdir/

test -e $tmpdir && rm -rf $tmpdir
mkdir $tmpdir
cp -r . ${tmpdir}/
find ${tmpdir} -iname "*.pyc"   -exec rm "{}" \;
find ${tmpdir} -iname "*.marks" -exec rm "{}" \;
find ${tmpdir} -iname "*~"      -exec rm "{}" \;
find ${tmpdir} -iname "*.svn"   -exec rm -rf "{}" \; 2>/dev/null
find ${tmpdir} -iname ".git*"      -exec rm -rf "{}" \;
find ${tmpdir} -iname "opsi-dev*" -exec rm "{}" \;
find ${tmpdir} -iname "tftp-hpa_*" -exec rm "{}" \;
find ${tmpdir} -iname "tftp-hpa-*" -exec rm -rf "{}" \;

cd ${tmpdir}/
./autogen.sh
./configure
dpkg-buildpackage -S -nc
mv ${tmpdir}/../${packagename}_${version}.tar.gz $destdir/
mv ${tmpdir}/../${packagename}_${version}.dsc    $destdir/
#rm -rf $tmpdir
echo "============================================================================================="
echo "source archive: ${destdir}/${packagename}_${version}.tar.gz"
echo "dsc file:       ${destdir}/${packagename}_${version}.dsc"
echo "spec file:      ${destdir}/${packagename}.spec"
echo "============================================================================================="
cd $cwd

