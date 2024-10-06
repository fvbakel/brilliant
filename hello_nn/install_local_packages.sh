#
# Purpose of this script is to copy that packages that are used used
# here but are from local sources
#
if [ -d ./graph ]; then 
    rm -r ./graph 
fi

cp -r ../hello_maze/graph ./

if [ -d ./basegrid ]; then 
    rm -r ./basegrid 
fi

cp -r ../hello_maze/basegrid ./

if [ -d ./gamegrid ]; then 
    rm -r ./gamegrid 
fi

cp -r ../hello_maze/gamegrid ./