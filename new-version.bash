#!/usr/bin/bash

# https://stackoverflow.com/a/13089269
#if [[ $1 == ?(-)+([[:digit:]]) ]] ;
#then
#    echo "num"
#cp snatcher.py versions/snatcher.py.v$1
#cp snatcher.conf versions/snatcher.conf.v$1
#cp www.py versions/www.py.v$1
#else
#    echo "non-num"
#fi

# https://stackoverflow.com/a/806923
re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
   echo "error: Not a number" >&2; exit 1
fi

if [ -f versions/snatcher.py.v$1 ] ||
   [ -f versions/snatcher.conf.v$1 ] ||
   [ -f versions/snatcher.js.v$1 ] ||
   [ -f versions/snatcher.css.v$1 ] ||
   [ -f versions/db.py.v$1 ] ||
   [ -f versions/snatcher_create.sql.v$1 ] ||
   [ -f versions/snatcher_user.sql.v$1 ] ||
   [ -f versions/snatcher_user.py.v$1 ] ||
   [ -f versions/counter.py.v$1 ] ||
   [ -f versions/snatcher.xcf.v$1 ] ||
   [ -f versions/snatcher.png.v$1 ] ||
   [ -f versions/snatcher.manifest.json.v$1 ] ||
   [ -f versions/www.py.v$1 ];
then
    echo "file exists"
fi

cp snatcher.py versions/snatcher.py.v$1
cp snatcher.conf versions/snatcher.conf.v$1
cp snatcher.js versions/snatcher.js.v$1
cp snatcher.css versions/snatcher.css.v$1
cp snatcher_user.sql versions/snatcher_user.sql.v$1
cp snatcher_user.py versions/snatcher_user.py.v$1
cp db.py versions/db.py.v$1
cp snatcher_create.sql versions/snatcher_create.sql.v$1
cp counter.py versions/counter.py.v$1
cp ReceiptSnatcherIcon/ReceiptSnatcher.xcf versions/snatcher.xcf.v$1
cp ReceiptSnatcherIcon/ReceiptSnatcher.png versions/snatcher.png.v$1
cp snatcher.manifest.json versions/snatcher.manifest.json.v$1
cp www.py versions/www.py.v$1

