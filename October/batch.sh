# mkdir 你自己的文件夹
# 复制test.sh到你自己的文件夹
# 把.apk文件传到你自己的文件夹(scp *.apk)
# 运行./test.sh
# 输出见wzq文件夹所示
suffix=".apk"
file_all=$(ls)
for file in $file_all
do
    if test -f $file
    then
    echo process file $file
    mkdir ${file%"$suffix"}
    path=`pwd`'/'
    echo $path$file
    cd ${file%"$suffix"}
    python3 ../../scripts/searchStr.py -i $path$file -o ./
    fi
    if test -d $file
    then
    continue
    fi
    cd ..
done
