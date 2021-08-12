# -*- coding:utf-8 -*-
#执行命令：python3 extract.py filepath function_name
#作用：查找对应函数名称在native中的位置，输出为对应.so文件名

if __name__ == "__main__":
    import sys
    import os
    print("name:", sys.argv[0])
    len = len(sys.argv)
    if len <= 2:
        print("arguments error，filepath or function name is need !!!")
        exit(0)
    os.system("strings -a -f "+sys.argv[1] + "\/*.so >out.txt")
    with open("out.txt", 'r', encoding='utf-8') as f:
        for line in f:
            if line.find(sys.argv[2]) != -1:
                print(line)