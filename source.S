.data
score: .int 76, 82, 90, 86, 79, 62
credit: .int 2, 2, 1, 2, 2, 3
label_0: .asciz "please input your student number:"
label_1: .asciz "%d"
label_6: .asciz "the score of student number %d is %f higher than 60.\n"
label_7: .asciz "the score of student number %d is %f lower than 60.\n"
.bss
.lcomm bss_tmp, 4
.lcomm stu_number, 4
.lcomm mean, 4
.lcomm sum, 4
.lcomm temp, 4
.lcomm i, 4
.text
.globl main
main:
finit
pushl $label_0
call printf
add $4, %esp
pushl $stu_number
pushl $label_1
call scanf
add $8, %esp
movl $0, sum
filds sum
fstps sum
movl $0, temp
movl $0, i
label_2:
movl i, %edi
movl $6, %esi
cmpl %esi, %edi
jae label_3
movl i, %edi
movl score(, %edi, 4), %eax
movl i, %edi
mull credit(, %edi, 4)
movl %eax, bss_tmp
flds sum
fiadd bss_tmp
fstps bss_tmp
flds bss_tmp
fstps sum
movl temp, %eax
movl i, %edi
addl credit(, %edi, 4), %eax
movl %eax, bss_tmp
movl bss_tmp, %edi
movl %edi, temp
incl i
jmp label_2
label_3:
flds sum
fidiv temp
fstps bss_tmp
flds bss_tmp
fstps mean
flds mean
movl $60, bss_tmp
fcom bss_tmp
jb label_4
flds mean
movl $60, bss_tmp
fisub bss_tmp
fstps bss_tmp
flds bss_tmp
fstps mean
flds mean
subl $8, %esp
fstpl (%esp)
pushl stu_number
pushl $label_6
call printf
add $16, %esp
jmp label_5
label_4:
movl $60, bss_tmp
flds mean
fsub mean
fstps bss_tmp
flds bss_tmp
fstps mean
flds mean
subl $8, %esp
fstpl (%esp)
pushl stu_number
pushl $label_7
call printf
add $16, %esp
label_5:
pushl $0
call exit
