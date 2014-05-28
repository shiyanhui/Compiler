#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2014-05-28 09:56:28
# @Last Modified by:   lime
# @Last Modified time: 2014-05-28 10:00:25

'''
Compiler for C language with python
    
Usage: python compiler.py -s [file] [options]

Options:
    -h, --h         show help
    -s file         import the source file, required!
    -l              lexer
    -p              parser
    -a              assembler, the assembler file is in the same path with compiler.py
    
Examples:
    python compiler.py -h
    python compiler.py -s source.c -a

Enjoy ^_^.
'''
import re
import sys
import getopt

# token比较大的分类
TOKEN_STYLE = ['KEY_WORD', 'IDENTIFIER', 'DIGIT_CONSTANT',
               'OPERATOR', 'SEPARATOR', 'STRING_CONSTANT']
# 将关键字、运算符、分隔符进行具体化
DETAIL_TOKEN_STYLE = {
    'include': 'INCLUDE', 'int': 'INT', 'float': 'FLOAT', 'char': 'CHAR', 'double': 'DOUBLE', 'for': 'FOR', 'if': 'IF', 'else': 'ELSE',
    'while': 'WHILE', 'do': 'DO', 'return': 'RETURN', '=': 'ASSIGN', '&': 'ADDRESS',
    '<': 'LT', '>': 'GT', '++': 'SELF_PLUS', '--': 'SELF_MINUS', '+': 'PLUS', '-': 'MINUS', '*': 'MUL', '/': 'DIV', '>=': 'GET', '<=': 'LET', '(': 'LL_BRACKET',
    ')': 'RL_BRACKET', '{': 'LB_BRACKET', '}': 'RB_BRACKET', '[': 'LM_BRACKET', ']': 'RM_BRACKET', ',': 'COMMA', '\"': 'DOUBLE_QUOTE',
    ';': 'SEMICOLON', '#': 'SHARP'}
# 关键字
keywords = [['int', 'float', 'double', 'char', 'void'],
           ['if', 'for', 'while', 'do', 'else'], ['include', 'return']]
# 运算符
operators = ['=', '&', '<', '>', '++', '--',
             '+', '-', '*', '/', '>=', '<=', '!=']
# 分隔符
delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

# c文件名字
file_name = None
# 文件内容
content = None


class Token(object):
    '''记录分析出来的单词'''

    def __init__(self, type_index, value):
        self.type = DETAIL_TOKEN_STYLE[
            value] if type_index == 0 or type_index == 3 or type_index == 4 else TOKEN_STYLE[type_index]
        self.value = value


class Lexer(object):
    '''词法分析器'''

    def __init__(self):
        # 用来保存词法分析出来的结果
        self.tokens = []

    # 判断是否是空白字符
    def is_blank(self, index):
        return content[index] == ' ' or content[index] == '\t' or content[index] == '\n' or content[index] == '\r'

    # 跳过空白字符
    def skip_blank(self, index):
        while index < len(content) and self.is_blank(index):
            index += 1
        return index

    # 打印
    def print_log(self, style, value):
        print '(%s, %s)' % (style, value)

    # 判断是否是关键字
    def is_keyword(self, value):
        for item in keywords:
            if value in item:
                return True
        return False

    # 词法分析主程序
    def main(self):
        i = 0
        while i < len(content):
            i = self.skip_blank(i)
            # 如果是引入头文件，还有一种可能是16进制数，这里先不判断
            if content[i] == '#':
                #self.print_log( '分隔符', content[ i ] )
                self.tokens.append(Token(4, content[i]))
                i = self.skip_blank(i + 1)
                # 分析这一引入头文件
                while i < len(content):
                    # 匹配"include"
                    if re.match('include', content[i:]):
                        # self.print_log( '关键字', 'include' )
                        self.tokens.append(Token(0, 'include'))
                        i = self.skip_blank(i + 7)
                    # 匹配"或者<
                    elif content[i] == '\"' or content[i] == '<':
                        # self.print_log( '分隔符', content[ i ] )
                        self.tokens.append(Token(4, content[i]))
                        i = self.skip_blank(i + 1)
                        close_flag = '\"' if content[i] == '\"' else '>'
                        # 找到include的头文件
                        lib = ''
                        while content[i] != close_flag:
                            lib += content[i]
                            i += 1
                        # self.print_log( '标识符', lib )
                        self.tokens.append(Token(1, lib))
                        # 跳出循环后，很显然找到close_flog
                        # self.print_log( '分隔符', close_flag )
                        self.tokens.append(Token(4, close_flag))
                        i = self.skip_blank(i + 1)
                        break
                    else:
                        print 'include error!'
                        exit()
            # 如果是字母或者是以下划线开头
            elif content[i].isalpha() or content[i] == '_':
                # 找到该字符串
                temp = ''
                while i < len(content) and (content[i].isalpha() or content[i] == '_' or content[i].isdigit()):
                    temp += content[i]
                    i += 1
                # 判断该字符串
                if self.is_keyword(temp):
                    # self.print_log( '关键字', temp )
                    self.tokens.append(Token(0, temp))
                else:
                    # self.print_log( '标识符', temp )
                    self.tokens.append(Token(1, temp))
                i = self.skip_blank(i)
            # 如果是数字开头
            elif content[i].isdigit():
                temp = ''
                while i < len(content):
                    if content[i].isdigit() or (content[i] == '.' and content[i + 1].isdigit()):
                        temp += content[i]
                        i += 1
                    elif not content[i].isdigit():
                        if content[i] == '.':
                            print 'float number error!'
                            exit()
                        else:
                            break
                # self.print_log( '常量' , temp )
                self.tokens.append(Token(2, temp))
                i = self.skip_blank(i)
            # 如果是分隔符
            elif content[i] in delimiters:
                # self.print_log( '分隔符', content[ i ] )
                self.tokens.append(Token(4, content[i]))
                # 如果是字符串常量
                if content[i] == '\"':
                    i += 1
                    temp = ''
                    while i < len(content):
                        if content[i] != '\"':
                            temp += content[i]
                            i += 1
                        else:
                            break
                    else:
                        print 'error:lack of \"'
                        exit()
                    # self.print_log( '常量' , temp )
                    self.tokens.append(Token(5, temp))
                    # self.print_log( '分隔符' , '\"' )
                    self.tokens.append(Token(4, '\"'))
                i = self.skip_blank(i + 1)
            # 如果是运算符
            elif content[i] in operators:
                # 如果是++或者--
                if (content[i] == '+' or content[i] == '-') and content[i + 1] == content[i]:
                    # self.print_log( '运算符', content[ i ] * 2 )
                    self.tokens.append(Token(3, content[i] * 2))
                    i = self.skip_blank(i + 2)
                # 如果是>=或者<=
                elif (content[i] == '>' or content[i] == '<') and content[i + 1] == '=':
                    # self.print_log( '运算符', content[ i ] + '=' )
                    self.tokens.append(Token(3, content[i] + '='))
                    i = self.skip_blank(i + 2)
                # 其他
                else:
                    # self.print_log( '运算符', content[ i ] )
                    self.tokens.append(Token(3, content[i]))
                    i = self.skip_blank(i + 1)


class SyntaxTreeNode(object):
    '''语法树节点'''

    def __init__(self, value=None, _type=None, extra_info=None):
        # 节点的值，为文法中的终结符或者非终结符
        self.value = value
        # 记录某些token的类型
        self.type = _type
        # 语义分析中记录关于token的其他一些信息，比如关键字是变量，该变量类型为int
        self.extra_info = extra_info
        self.father = None
        self.left = None
        self.right = None
        self.first_son = None
    # 设置value

    def set_value(self, value):
        self.value = value
    # 设置type

    def set_type(self, _type):
        self.type = _type
    # 设置extra_info

    def set_extra_info(self, extra_info):
        self.extra_info = extra_info


class SyntaxTree(object):
    '''语法树'''

    def __init__(self):
        # 树的根节点
        self.root = None
        # 现在遍历到的节点
        self.current = None

    # 添加一个子节点，必须确定father在该树中
    def add_child_node(self, new_node, father=None):
        if not father:
            father = self.current
        # 认祖归宗
        new_node.father = father
        # 如果father节点没有儿子，则将其赋值为其第一个儿子
        if not father.first_son:
            father.first_son = new_node
        else:
            current_node = father.first_son
            while current_node.right:
                current_node = current_node.right
            current_node.right = new_node
            new_node.left = current_node
        self.current = new_node

    # 交换相邻的两棵兄弟子树
    def switch(self, left, right):
        left_left = left.left
        right_right = right.right
        left.left = right
        left.right = right_right
        right.left = left_left
        right.right = left
        if left_left:
            left_left.right = right
        if right_right:
            right_right.left = left


class Parser(object):
    '''语法分析器'''

    def __init__(self):
        lexer = Lexer()
        lexer.main()
        # 要分析的tokens
        self.tokens = lexer.tokens
        # tokens下标
        self.index = 0
        # 最终生成的语法树
        self.tree = SyntaxTree()

    # 处理大括号里的部分
    def _block(self, father_tree):
        self.index += 1
        sentence_tree = SyntaxTree()
        sentence_tree.current = sentence_tree.root = SyntaxTreeNode('Sentence')
        father_tree.add_child_node(sentence_tree.root, father_tree.root)
        while True:
            # 句型
            sentence_pattern = self._judge_sentence_pattern()
            # 声明语句
            if sentence_pattern == 'STATEMENT':
                self._statement(sentence_tree.root)
            # 赋值语句
            elif sentence_pattern == 'ASSIGNMENT':
                self._assignment(sentence_tree.root)
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call(sentence_tree.root)
            # 控制流语句
            elif sentence_pattern == 'CONTROL':
                self._control(sentence_tree.root)
            # return语句
            elif sentence_pattern == 'RETURN':
                self._return(sentence_tree.root)
            # 右大括号，函数结束
            elif sentence_pattern == 'RB_BRACKET':
                break
            else:
                print 'block error!'
                exit()

    # include句型
    def _include(self, father=None):
        if not father:
            father = self.tree.root
        include_tree = SyntaxTree()
        include_tree.current = include_tree.root = SyntaxTreeNode('Include')
        self.tree.add_child_node(include_tree.root, father)
        # include语句中双引号的个数
        cnt = 0
        # include语句是否结束
        flag = True
        while flag:
            if self.tokens[self.index] == '\"':
                cnt += 1
            if self.index >= len(self.tokens) or cnt >= 2 or self.tokens[self.index].value == '>':
                flag = False
            include_tree.add_child_node(
                SyntaxTreeNode(self.tokens[self.index].value), include_tree.root)
            self.index += 1

    # 函数声明
    def _function_statement(self, father=None):
        if not father:
            father = self.tree.root
        func_statement_tree = SyntaxTree()
        func_statement_tree.current = func_statement_tree.root = SyntaxTreeNode(
            'FunctionStatement')
        self.tree.add_child_node(func_statement_tree.root, father)
        # 函数声明语句什么时候结束
        flag = True
        while flag and self.index < len(self.tokens):
            # 如果是函数返回类型
            if self.tokens[self.index].value in keywords[0]:
                return_type = SyntaxTreeNode('Type')
                func_statement_tree.add_child_node(return_type)
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
                self.index += 1
            # 如果是函数名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                func_name = SyntaxTreeNode('FunctionName')
                func_statement_tree.add_child_node(
                    func_name, func_statement_tree.root)
                # extra_info
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {'type': 'FUNCTION_NAME'}))
                self.index += 1
            # 如果是参数序列
            elif self.tokens[self.index].type == 'LL_BRACKET':
                params_list = SyntaxTreeNode('StateParameterList')
                func_statement_tree.add_child_node(
                    params_list, func_statement_tree.root)
                self.index += 1
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].value in keywords[0]:
                        param = SyntaxTreeNode('Parameter')
                        func_statement_tree.add_child_node(param, params_list)
                        # extra_info
                        func_statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}), param)
                        if self.tokens[self.index + 1].type == 'IDENTIFIER':
                            # extra_info
                            func_statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index + 1].value, 'IDENTIFIER', {
                                                               'type': 'VARIABLE', 'variable_type': self.tokens[self.index].value}), param)
                        else:
                            print '函数定义参数错误！'
                            exit()
                        self.index += 1
                    self.index += 1
                self.index += 1
            # 如果是遇见了左大括号
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self._block(func_statement_tree)

    # 声明语句
    def _statement(self, father=None):
        if not father:
            father = self.tree.root
        statement_tree = SyntaxTree()
        statement_tree.current = statement_tree.root = SyntaxTreeNode(
            'Statement')
        self.tree.add_child_node(statement_tree.root, father)
        # 暂时用来保存当前声明语句的类型，以便于识别多个变量的声明
        tmp_variable_type = None
        while self.tokens[self.index].type != 'SEMICOLON':
            # 变量类型
            if self.tokens[self.index].value in keywords[0]:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = SyntaxTreeNode('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            # 变量名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # extra_info
                statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                              'type': 'VARIABLE', 'variable_type': tmp_variable_type}), statement_tree.root)
            # 数组大小
            elif self.tokens[self.index].type == 'DIGIT_CONSTANT':
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), statement_tree.root)
                statement_tree.current.left.set_extra_info(
                    {'type': 'LIST', 'list_type': tmp_variable_type})
            # 数组元素
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self.index += 1
                constant_list = SyntaxTreeNode('ConstantList')
                statement_tree.add_child_node(
                    constant_list, statement_tree.root)
                while self.tokens[self.index].type != 'RB_BRACKET':
                    if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                        statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), constant_list)
                    self.index += 1
            # 多个变量声明
            elif self.tokens[self.index].type == 'COMMA':
                while self.tokens[self.index].type != 'SEMICOLON':
                    if self.tokens[self.index].type == 'IDENTIFIER':
                        tree = SyntaxTree()
                        tree.current = tree.root = SyntaxTreeNode('Statement')
                        self.tree.add_child_node(tree.root, father)
                        # 类型
                        variable_type = SyntaxTreeNode('Type')
                        tree.add_child_node(variable_type)
                        # extra_info
                        # 类型
                        tree.add_child_node(
                            SyntaxTreeNode(tmp_variable_type, 'FIELD_TYPE', {'type': tmp_variable_type}))
                        # 变量名
                        tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                            'type': 'VARIABLE', 'variable_type': tmp_variable_type}), tree.root)
                    self.index += 1
                break
            self.index += 1
        self.index += 1

    # 赋值语句-->TODO
    def _assignment(self, father=None):
        if not father:
            father = self.tree.root
        assign_tree = SyntaxTree()
        assign_tree.current = assign_tree.root = SyntaxTreeNode('Assignment')
        self.tree.add_child_node(assign_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'IDENTIFIER':
                assign_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER'))
                self.index += 1
            elif self.tokens[self.index].type == 'ASSIGN':
                self.index += 1
                self._expression(assign_tree.root)
        self.index += 1

    # while语句，没处理do-while的情况，只处理了while
    def _while(self, father=None):
        while_tree = SyntaxTree()
        while_tree.current = while_tree.root = SyntaxTreeNode(
            'Control', 'WhileControl')
        self.tree.add_child_node(while_tree.root, father)

        self.index += 1
        if self.tokens[self.index].type == 'LL_BRACKET':
            tmp_index = self.index
            while self.tokens[tmp_index].type != 'RL_BRACKET':
                tmp_index += 1
            self._expression(while_tree.root, tmp_index)

            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(while_tree)

    # for语句
    def _for(self, father=None):
        for_tree = SyntaxTree()
        for_tree.current = for_tree.root = SyntaxTreeNode(
            'Control', 'ForControl')
        self.tree.add_child_node(for_tree.root, father)
        # 标记for语句是否结束
        while True:
            token_type = self.tokens[self.index].type
            # for标记
            if token_type == 'FOR':
                self.index += 1
            # 左小括号
            elif token_type == 'LL_BRACKET':
                self.index += 1
                # 首先找到右小括号的位置
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                # for语句中的第一个分号前的部分
                self._assignment(for_tree.root)
                # 两个分号中间的部分
                self._expression(for_tree.root)
                self.index += 1
                # 第二个分号后的部分
                self._expression(for_tree.root, tmp_index)
                self.index += 1
            # 如果为左大括号
            elif token_type == 'LB_BRACKET':
                self._block(for_tree)
                break
        # 交换for语句下第三个子节点和第四个子节点
        current_node = for_tree.root.first_son.right.right
        next_node = current_node.right
        for_tree.switch(current_node, next_node)

    # if语句
    def _if_else(self, father=None):
        if_else_tree = SyntaxTree()
        if_else_tree.current = if_else_tree.root = SyntaxTreeNode(
            'Control', 'IfElseControl')
        self.tree.add_child_node(if_else_tree.root, father)

        if_tree = SyntaxTree()
        if_tree.current = if_tree.root = SyntaxTreeNode('IfControl')
        if_else_tree.add_child_node(if_tree.root)

        # if标志
        if self.tokens[self.index].type == 'IF':
            self.index += 1
            # 左小括号
            if self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                # 右小括号位置
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                self._expression(if_tree.root, tmp_index)
                self.index += 1
            else:
                print 'error: lack of left bracket!'
                exit()

            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(if_tree)

        # 如果是else关键字
        if self.tokens[self.index].type == 'ELSE':
            self.index += 1
            else_tree = SyntaxTree()
            else_tree.current = else_tree.root = SyntaxTreeNode('ElseControl')
            if_else_tree.add_child_node(else_tree.root, if_else_tree.root)
            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(else_tree)

    def _control(self, father=None):
        token_type = self.tokens[self.index].type
        if token_type == 'WHILE' or token_type == 'DO':
            self._while(father)
        elif token_type == 'IF':
            self._if_else(father)
        elif token_type == 'FOR':
            self._for(father)
        else:
            print 'error: control style not supported!'
            exit()

    # 表达式-->TODO
    def _expression(self, father=None, index=None):
        if not father:
            father = self.tree.root
        # 运算符优先级
        operator_priority = {'>': 0, '<': 0, '>=': 0, '<=': 0,
                             '+': 1, '-': 1, '*': 2, '/': 2, '++': 3, '--': 3, '!': 3}
        # 运算符栈
        operator_stack = []
        # 转换成的逆波兰表达式结果
        reverse_polish_expression = []
        # 中缀表达式转为后缀表达式，即逆波兰表达式
        while self.tokens[self.index].type != 'SEMICOLON':
            if index and self.index >= index:
                break
            # 如果是常量
            if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Constant'))
                reverse_polish_expression.append(tree)
            # 如果是变量或者数组的某元素
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # 变量
                if self.tokens[self.index + 1].value in operators or self.tokens[self.index + 1].type == 'SEMICOLON':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'Variable')
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_Variable'))
                    reverse_polish_expression.append(tree)
                # 数组的某一个元素ID[i]
                elif self.tokens[self.index + 1].type == 'LM_BRACKET':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'ArrayItem')
                    # 数组的名字
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_ArrayName'))
                    self.index += 2
                    if self.tokens[self.index].type != 'DIGIT_CONSTANT' and self.tokens[self.index].type != 'IDENTIFIER':
                        print 'error: 数组下表必须为常量或标识符'
                        print self.tokens[self.index].type
                        exit()
                    else:
                        # 数组下标
                        tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, '_ArrayIndex'), tree.root)
                        reverse_polish_expression.append(tree)
            # 如果是运算符
            elif self.tokens[self.index].value in operators or self.tokens[self.index].type == 'LL_BRACKET' or self.tokens[self.index].type == 'RL_BRACKET':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Operator', 'Operator')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Operator'))
                # 如果是左括号，直接压栈
                if self.tokens[self.index].type == 'LL_BRACKET':
                    operator_stack.append(tree.root)
                # 如果是右括号，弹栈直到遇到左括号为止
                elif self.tokens[self.index].type == 'RL_BRACKET':
                    while operator_stack and operator_stack[-1].current.type != 'LL_BRACKET':
                        reverse_polish_expression.append(operator_stack.pop())
                    # 将左括号弹出来
                    if operator_stack:
                        operator_stack.pop()
                # 其他只能是运算符
                else:
                    while operator_stack and operator_priority[tree.current.value] < operator_priority[operator_stack[-1].current.value]:
                        reverse_polish_expression.append(operator_stack.pop())
                    operator_stack.append(tree)
            self.index += 1
        # 最后将符号栈清空，最终得到逆波兰表达式reverse_polish_expression
        while operator_stack:
            reverse_polish_expression.append(operator_stack.pop())
        # 打印
        # for item in reverse_polish_expression:
        #   print item.current.value,
        # print

        # 操作数栈
        operand_stack = []
        child_operators = [['!', '++', '--'], [
            '+', '-', '*', '/', '>', '<', '>=', '<=']]
        for item in reverse_polish_expression:
            if item.root.type != 'Operator':
                operand_stack.append(item)
            else:
                # 处理单目运算符
                if item.current.value in child_operators[0]:
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'SingleOperand')
                    # 添加操作符
                    new_tree.add_child_node(item.root)
                    # 添加操作数
                    new_tree.add_child_node(a.root, new_tree.root)
                    operand_stack.append(new_tree)
                # 双目运算符
                elif item.current.value in child_operators[1]:
                    b = operand_stack.pop()
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'DoubleOperand')
                    # 第一个操作数
                    new_tree.add_child_node(a.root)
                    # 操作符
                    new_tree.add_child_node(item.root, new_tree.root)
                    # 第二个操作数
                    new_tree.add_child_node(b.root, new_tree.root)
                    operand_stack.append(new_tree)
                else:
                    print 'operator %s not supported!' % item.current.value
                    exit()
        self.tree.add_child_node(operand_stack[0].root, father)

    # 函数调用
    def _function_call(self, father=None):
        if not father:
            father = self.tree.root
        func_call_tree = SyntaxTree()
        func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
            'FunctionCall')
        self.tree.add_child_node(func_call_tree.root, father)

        while self.tokens[self.index].type != 'SEMICOLON':
            # 函数名
            if self.tokens[self.index].type == 'IDENTIFIER':
                func_call_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
            # 左小括号
            elif self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                params_list = SyntaxTreeNode('CallParameterList')
                func_call_tree.add_child_node(params_list, func_call_tree.root)
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                    elif self.tokens[self.index].type == 'DOUBLE_QUOTE':
                        self.index += 1
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                        self.index += 1
                    elif self.tokens[self.index].type == 'ADDRESS':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'ADDRESS'), params_list)
                    self.index += 1
            else:
                print 'function call error!'
                exit()
            self.index += 1
        self.index += 1

    # return语句 -->TODO
    def _return(self, father=None):
        if not father:
            father = self.tree.root
        return_tree = SyntaxTree()
        return_tree.current = return_tree.root = SyntaxTreeNode('Return')
        self.tree.add_child_node(return_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'RETURN':
                return_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value))
                self.index += 1
            else:
                self._expression(return_tree.root)
        self.index += 1

    # 根据一个句型的句首判断句型
    def _judge_sentence_pattern(self):
        token_value = self.tokens[self.index].value
        token_type = self.tokens[self.index].type
        # include句型
        if token_type == 'SHARP' and self.tokens[self.index + 1].type == 'INCLUDE':
            return 'INCLUDE'
        # 控制句型
        elif token_value in keywords[1]:
            return 'CONTROL'
        # 有可能是声明语句或者函数声明语句
        elif token_value in keywords[0] and self.tokens[self.index + 1].type == 'IDENTIFIER':
            index_2_token_type = self.tokens[self.index + 2].type
            if index_2_token_type == 'LL_BRACKET':
                return 'FUNCTION_STATEMENT'
            elif index_2_token_type == 'SEMICOLON' or index_2_token_type == 'LM_BRACKET' or index_2_token_type == 'COMMA':
                return 'STATEMENT'
            else:
                return 'ERROR'
        # 可能为函数调用或者赋值语句
        elif token_type == 'IDENTIFIER':
            index_1_token_type = self.tokens[self.index + 1].type
            if index_1_token_type == 'LL_BRACKET':
                return 'FUNCTION_CALL'
            elif index_1_token_type == 'ASSIGN':
                return 'ASSIGNMENT'
            else:
                return 'ERROR'
        # return语句
        elif token_type == 'RETURN':
            return 'RETURN'
        # 右大括号，表明函数的结束
        elif token_type == 'RB_BRACKET':
            self.index += 1
            return 'RB_BRACKET'
        else:
            return 'ERROR'

    # 主程序
    def main(self):
        # 根节点
        self.tree.current = self.tree.root = SyntaxTreeNode('Sentence')
        while self.index < len(self.tokens):
            # 句型
            sentence_pattern = self._judge_sentence_pattern()
            # 如果是include句型
            if sentence_pattern == 'INCLUDE':
                self._include()
            # 函数声明语句
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement()
                break
            # 声明语句
            elif sentence_pattern == 'STATEMENT':
                self._statement()
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call()
            else:
                print 'main error!'
                exit()

    # DFS遍历语法树
    def display(self, node):
        if not node:
            return
        print '( self: %s %s, father: %s, left: %s, right: %s )' % (node.value, node.type, node.father.value if node.father else None, node.left.value if node.left else None, node.right.value if node.right else None)
        child = node.first_son
        while child:
            self.display(child)
            child = child.right


class AssemblerFileHandler(object):
    '''维护生成的汇编文件'''

    def __init__(self):
        self.result = ['.data', '.bss', '.lcomm bss_tmp, 4', '.text']
        self.data_pointer = 1
        self.bss_pointer = 3
        self.text_pointer = 4

    def insert(self, value, _type):
        # 插入到data域
        if _type == 'DATA':
            self.result.insert(self.data_pointer, value)
            self.data_pointer += 1
            self.bss_pointer += 1
            self.text_pointer += 1
        # 插入到bss域
        elif _type == 'BSS':
            self.result.insert(self.bss_pointer, value)
            self.bss_pointer += 1
            self.text_pointer += 1
        # 插入到代码段
        elif _type == 'TEXT':
            self.result.insert(self.text_pointer, value)
            self.text_pointer += 1
        else:
            print 'error!'
            exit()

    # 将结果保存到文件中
    def generate_ass_file(self):
        self.file = open(file_name + '.S', 'w+')
        self.file.write('\n'.join(self.result) + '\n')
        self.file.close()


class Assembler(object):
    '''编译成汇编语言'''

    def __init__(self):
        self.parser = Parser()
        self.parser.main()
        # 生成的语法树
        self.tree = self.parser.tree
        # 要生成的汇编文件管理器
        self.ass_file_handler = AssemblerFileHandler()
        # 符号表
        self.symbol_table = {}
        # 语法类型
        self.sentence_type = ['Sentence', 'Include', 'FunctionStatement',
                              'Statement', 'FunctionCall', 'Assignment', 'Control', 'Expression', 'Return']
        # 表达式中的符号栈
        self.operator_stack = []
        # 表达式中的操作符栈
        self.operand_stack = []
        # 已经声明了多少个label
        self.label_cnt = 0
        # ifelse中的标签
        self.labels_ifelse = {}

    # include句型
    def _include(self, node=None):
        pass

    # 函数定义句型
    def _function_statement(self, node=None):
        # 第一个儿子
        current_node = node.first_son
        while current_node:
            if current_node.value == 'FunctionName':
                if current_node.first_son.value != 'main':
                    print 'other function statement except for main is not supported!'
                    exit()
                else:
                    self.ass_file_handler.insert('.globl main', 'TEXT')
                    self.ass_file_handler.insert('main:', 'TEXT')
                    self.ass_file_handler.insert('finit', 'TEXT')
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right

    # 简单的sizeof
    def _sizeof(self, _type):
        size = -1
        if _type == 'int' or _type == 'float' or _type == 'long':
            size = 4
        elif _type == 'char':
            size = 1
        elif _type == 'double':
            size = 8
        return str(size)

    # 声明语句
    def _statement(self, node=None):
        # 对应的汇编代码中的声明语句
        line = None
        # 1:初始化的，0:没有初始化
        flag = 0
        # 变量数据类型
        variable_field_type = None
        # 变量类型，是数组还是单个变量
        variable_type = None
        # 变量名
        variable_name = None
        current_node = node.first_son
        while current_node:
            # 类型
            if current_node.value == 'Type':
                variable_field_type = current_node.first_son.value
            # 变量名
            elif current_node.type == 'IDENTIFIER':
                variable_name = current_node.value
                variable_type = current_node.extra_info['type']
                line = '.lcomm ' + variable_name + \
                    ', ' + self._sizeof(variable_field_type)
            # 数组元素
            elif current_node.value == 'ConstantList':
                line = variable_name + ': .' + variable_field_type + ' '
                tmp_node = current_node.first_son
                # 保存该数组
                array = []
                while tmp_node:
                    array.append(tmp_node.value)
                    tmp_node = tmp_node.right
                line += ', '.join(array)
            current_node = current_node.right
        self.ass_file_handler.insert(
            line, 'BSS' if variable_type == 'VARIABLE' else 'DATA')
        # 将该变量存入符号表
        self.symbol_table[variable_name] = {
            'type': variable_type, 'field_type': variable_field_type}

    # 函数调用
    def _function_call(self, node=None):
        current_node = node.first_son
        func_name = None
        parameter_list = []
        while current_node:
            # 函数名字
            if current_node.type == 'FUNCTION_NAME':
                func_name = current_node.value
                if func_name != 'scanf' and func_name != 'printf':
                    print 'function call except scanf and printf not supported yet!'
                    exit()
            # 函数参数
            elif current_node.value == 'CallParameterList':
                tmp_node = current_node.first_son
                while tmp_node:
                    # 是常数
                    if tmp_node.type == 'DIGIT_CONSTANT' or tmp_node.type == 'STRING_CONSTANT':
                        # 汇编中该参数的名称
                        label = 'label_' + str(self.label_cnt)
                        self.label_cnt += 1
                        if tmp_node.type == 'STRING_CONSTANT':
                            # 添加数据段中该参数定义
                            line = label + ': .asciz "' + tmp_node.value + '"'
                            self.ass_file_handler.insert(line, 'DATA')
                        else:
                            print 'in functionc_call digital constant parameter is not supported yet!'
                            exit()
                        self.symbol_table[label] = {
                            'type': 'STRING_CONSTANT', 'value': tmp_node.value}
                        parameter_list.append(label)
                    # 是某个变量
                    elif tmp_node.type == 'IDENTIFIER':
                        parameter_list.append(tmp_node.value)
                    elif tmp_node.type == 'ADDRESS':
                        pass
                    else:
                        print tmp_node.value
                        print tmp_node.type
                        print 'parameter type is not supported yet!'
                        exit()
                    tmp_node = tmp_node.right
            current_node = current_node.right
        # 添加到代码段
        if func_name == 'printf':
            #%esp要+的值
            num = 0
            for parameter in parameter_list[::-1]:
                # 如果该参数的类型是字符串常量
                if self.symbol_table[parameter]['type'] == 'STRING_CONSTANT':
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                    num += 1
                elif self.symbol_table[parameter]['type'] == 'VARIABLE':
                    field_type = self.symbol_table[parameter]['field_type']
                    if field_type == 'int':
                        line = 'pushl ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 1
                    elif field_type == 'float':
                        line = 'flds ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'subl $8, %esp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'fstpl (%esp)'
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 2
                    else:
                        print 'field type except int and float is not supported yet!'
                        exit()
                else:
                    print 'parameter type not supported in printf yet!'
                    exit()
            line = 'call printf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
        elif func_name == 'scanf':
            num = 0
            for parameter in parameter_list[::-1]:
                parameter_type = self.symbol_table[parameter]['type']
                if parameter_type == 'STRING_CONSTANT' or parameter_type == 'VARIABLE':
                    num += 1
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    print 'parameter type not supported in scanf!'
                    exit()
            line = 'call scanf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
    # 赋值语句

    def _assignment(self, node=None):
        current_node = node.first_son
        if current_node.type == 'IDENTIFIER' and current_node.right.value == 'Expression':
            expres = self._expression(current_node.right)
            # 该变量的类型
            field_type = self.symbol_table[current_node.value]['field_type']
            if field_type == 'int':
                # 常数
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                elif expres['type'] == 'VARIABLE':
                    line = 'movl ' + expres['value'] + ', ' + '%edi'
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'movl %edi, ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    pass
            elif field_type == 'float':
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'filds ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
            else:
                print 'field type except int and float not supported!'
                exit()
        else:
            print 'assignment wrong.'
            exit()

    # for语句
    def _control_for(self, node=None):
        current_node = node.first_son
        # 遍历的是for循环中的那个部分
        cnt = 2
        while current_node:
            # for第一部分
            if current_node.value == 'Assignment':
                self._assignment(current_node)
            # for第二、三部分
            elif current_node.value == 'Expression':
                if cnt == 2:
                    cnt += 1
                    line = 'label_' + str(self.label_cnt) + ':'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.label_cnt += 1
                    self._expression(current_node)
                else:
                    self._expression(current_node)
            # for语句部分
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right
        line = 'jmp label_' + str(self.label_cnt - 1)
        self.ass_file_handler.insert(line, 'TEXT')
        line = 'label_' + str(self.label_cnt) + ':'
        self.ass_file_handler.insert(line, 'TEXT')
        self.label_cnt += 1

    # if else语句
    def _control_if(self, node=None):
        current_node = node.first_son
        self.labels_ifelse['label_else'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        self.labels_ifelse['label_end'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        while current_node:
            if current_node.value == 'IfControl':
                if current_node.first_son.value != 'Expression' or current_node.first_son.right.value != 'Sentence':
                    print 'control_if error!'
                    exit()
                self._expression(current_node.first_son)
                self.traverse(current_node.first_son.right.first_son)
                line = 'jmp ' + self.labels_ifelse['label_end']
                self.ass_file_handler.insert(line, 'TEXT')
                line = self.labels_ifelse['label_else'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            elif current_node.value == 'ElseControl':
                self.traverse(current_node.first_son)
                line = self.labels_ifelse['label_end'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            current_node = current_node.right

    # while语句
    def _control_while(self, node=None):
        print 'while not supported yet!'

    # return语句
    def _return(self, node=None):
        current_node = node.first_son
        if current_node.value != 'return' or current_node.right.value != 'Expression':
            print 'return error!'
            exit()
        else:
            current_node = current_node.right
            expres = self._expression(current_node)
            if expres['type'] == 'CONSTANT':
                line = 'pushl $' + expres['value']
                self.ass_file_handler.insert(line, 'TEXT')
                line = 'call exit'
                self.ass_file_handler.insert(line, 'TEXT')
            else:
                print 'return type not supported!'
                exit()

    # 遍历表达式
    def _traverse_expression(self, node=None):
        if not node:
            return
        if node.type == '_Variable':
            self.operand_stack.append(
                {'type': 'VARIABLE', 'operand': node.value})
        elif node.type == '_Constant':
            self.operand_stack.append(
                {'type': 'CONSTANT', 'operand': node.value})
        elif node.type == '_Operator':
            self.operator_stack.append(node.value)
        elif node.type == '_ArrayName':
            self.operand_stack.append(
                {'type': 'ARRAY_ITEM', 'operand': [node.value, node.right.value]})
            return
        current_node = node.first_son
        while current_node:
            self._traverse_expression(current_node)
            current_node = current_node.right

    # 判断一个变量是不是float类型
    def _is_float(self, operand):
        return operand['type'] == 'VARIABLE' and self.symbol_table[operand['operand']]['field_type'] == 'float'
    # 判断两个操作数中是否含有float类型的数

    def _contain_float(self, operand_a, operand_b):
        return self._is_float(operand_a) or self._is_float(operand_b)

    # 表达式
    def _expression(self, node=None):
        if node.type == 'Constant':
            return {'type': 'CONSTANT', 'value': node.first_son.value}
        # 先清空
        self.operator_priority = []
        self.operand_stack = []
        # 遍历该表达式
        self._traverse_expression(node)

        # 双目运算符
        double_operators = ['+', '-', '*', '/', '>', '<', '>=', '<=']
        # 单目运算符
        single_operators = ['++', '--']
        # 运算符对汇编指令的映射
        operator_map = {'>': 'jbe', '<': 'jae', '>=': 'jb', '<=': 'ja'}
        while self.operator_stack:
            operator = self.operator_stack.pop()
            if operator in double_operators:
                operand_b = self.operand_stack.pop()
                operand_a = self.operand_stack.pop()
                contain_float = self._contain_float(operand_a, operand_b)
                if operator == '+':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'fadd ' if self._is_float(
                            operand_b) else 'fiadd '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        # 计算结果保存到bss_tmp中
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        # 第一个操作数
                        if operand_a['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_a['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'movl ' + \
                                operand_a['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_a['type'] == 'VARIABLE':
                            line = 'movl ' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_a['type'] == 'CONSTANT':
                            line = 'movl $' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        # 加上第二个操作数
                        if operand_b['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_b['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'addl ' + \
                                operand_b['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_b['type'] == 'VARIABLE':
                            line = 'addl ' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_b['type'] == 'CONSTANT':
                            line = 'addl $' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        # 赋值给临时操作数
                        line = 'movl %eax, bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'int'}

                elif operator == '-':
                    if contain_float:
                        # 操作数a
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        else:
                            if operand_a['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_a['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        # 操作数b
                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_b) else 'filds '
                                line += operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fsub ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fisub bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        # 计算结果保存到bss_tmp中
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        print 'not supported yet!'
                        exit()
                # 尚未考虑浮点数，只考虑整数乘法
                elif operator == '*':
                    if operand_a['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_a['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'movl ' + \
                            operand_a['operand'][0] + r'(, %edi, 4), %eax'
                        self.ass_file_handler.insert(line, 'TEXT')
                    else:
                        print 'other MUL not supported yet!'
                        exit()

                    if operand_b['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_b['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 相乘
                        line = 'mull ' + \
                            operand_b['operand'][0] + '(, %edi, 4)'
                        self.ass_file_handler.insert(line, 'TEXT')
                    else:
                        print 'other MUL not supported yet!'
                        exit()
                    # 将所得结果压入栈
                    line = r'movl %eax, bss_tmp'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.operand_stack.append(
                        {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                    self.symbol_table['bss_tmp'] = {
                        'type': 'IDENTIFIER', 'field_type': 'int'}
                elif operator == '/':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'fdiv ' if self._is_float(
                            operand_b) else 'fidiv '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        # 计算结果保存到bss_tmp中
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        pass
                elif operator == '>=':
                    if contain_float:
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                print 'array item not supported when >='
                                exit()
                        else:
                            pass

                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'fcom ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                print 'array item not supported when >='
                                exit()
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fcom bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = operator_map[
                                    '>='] + ' ' + self.labels_ifelse['label_else']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                    else:
                        pass
                elif operator == '<':
                    if contain_float:
                        pass
                    else:
                        line = 'movl $' if operand_a[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_a['operand'] + ', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'movl $' if operand_b[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_b['operand'] + ', %esi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = r'cmpl %esi, %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = operator_map[
                            '<'] + ' ' + 'label_' + str(self.label_cnt)
                        self.ass_file_handler.insert(line, 'TEXT')

            elif operator in single_operators:
                operand = self.operand_stack.pop()
                if operator == '++':
                    line = 'incl ' + operand['operand']
                    self.ass_file_handler.insert(line, 'TEXT')
                elif operator == '--':
                    pass
            else:
                print 'operator not supported!'
                exit()
        result = {'type': self.operand_stack[0]['type'], 'value': self.operand_stack[
            0]['operand']} if self.operand_stack else {'type': '', 'value': ''}
        return result

    # 处理某一种句型
    def _handler_block(self, node=None):
        if not node:
            return
        # 下一个将要遍历的节点
        if node.value in self.sentence_type:
            # 如果是根节点
            if node.value == 'Sentence':
                self.traverse(node.first_son)
            # include语句
            elif node.value == 'Include':
                self._include(node)
            # 函数声明
            elif node.value == 'FunctionStatement':
                self._function_statement(node)
            # 声明语句
            elif node.value == 'Statement':
                self._statement(node)
            # 函数调用
            elif node.value == 'FunctionCall':
                self._function_call(node)
            # 赋值语句
            elif node.value == 'Assignment':
                self._assignment(node)
            # 控制语句
            elif node.value == 'Control':
                if node.type == 'IfElseControl':
                    self._control_if(node)
                elif node.type == 'ForControl':
                    self._control_for(node)
                elif node.type == 'WhileControl':
                    self._control_while()
                else:
                    print 'control type not supported!'
                    exit()
            # 表达式语句
            elif node.value == 'Expression':
                self._expression(node)
            # return语句
            elif node.value == 'Return':
                self._return(node)
            else:
                print 'sentenct type not supported yet！'
                exit()

    # 遍历节点
    def traverse(self, node=None):
        self._handler_block(node)
        next_node = node.right
        while next_node:
            self._handler_block(next_node)
            next_node = next_node.right


def lexer():
    lexer = Lexer()
    lexer.main()
    for token in lexer.tokens:
        print '(%s, %s)' % (token.type, token.value)


def parser():
    parser = Parser()
    parser.main()
    parser.display(parser.tree.root)


def assembler():
    assem = Assembler()
    assem.traverse(assem.tree.root)
    assem.ass_file_handler.generate_ass_file()

if __name__ == '__main__':
    try:
        opts, argvs = getopt.getopt(sys.argv[1:], 's:lpah', ['help'])
    except:
        print __doc__
        exit()

    for opt, argv in opts:
        if opt in ['-h', '--h', '--help']:
            print __doc__
            exit()
        elif opt == '-s':
            file_name = argv.split('.')[0]
            source_file = open(argv, 'r')
            content = source_file.read()
        elif opt == '-l':
            lexer()
        elif opt == '-p':
            parser()
        elif opt == '-a':
            assembler()
