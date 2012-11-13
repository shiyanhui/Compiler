编译C语言的一个小型编译器
=========================
详细要求见http://blog.hit.edu.cn/jsx/post/46.html


LOGS:
-----

--------V2.0------------
1、支持词法分析、语法分析、语义分析、生成汇编
2、最终输出AT&T格式的汇编代码

--------V1.0------------
1、实现了基本的词法分析和语法分析
2、输出Tokens和语法分析树



用法(假设源文件为source.c)
------------------------
帮助：
python compiler.py -h

查看词法分析结果：
python compiler.py -s source.c -l

查看语法树：
python compiler.py -s source.c -p

生成汇编：
python compiler.py -s source.c -a
生成的汇编文件为source.S，与compiler.py同目录

将汇编文件编译成二进制：
gcc source.S -o source



注意：
------------------------
生成的汇编文件仅能在linux在编译，OS X虽然是unix like，
但是其gcc编译器与linux下的生成语法不同



TODO:
------------------------
只实现了该网站中出现的语法句型，还有很多语法状态没有实现。
比如，不支持嵌套的控制语句等。


Test Environment
------------------------
Ubuntu 12.04
Python version: 2.7


Contact me：
------------------------
shiyanhui66@gmail.com