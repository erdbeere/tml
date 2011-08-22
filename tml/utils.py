#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    A library which makes it possible to read teeworlds map files.

    :copyright: 2010-2011 by the TML Team, see AUTHORS for more details.
    :license: GNU GPL, see LICENSE for more details.
"""

def int32(x):
    if x>0xFFFFFFFF:
        raise OverflowError
    if x>0x7FFFFFFF:
        x=int(0x100000000-x)
        if x<2147483648:
            return -x
        else:
            return -2147483648
    return x

def ints_to_string(num):
    string = ''
    for val in num:
        string += chr(max(0, min(((val>>24)&0xff)-128, 255)))
        string += chr(max(0, min(((val>>16)&0xff)-128, 255)))
        string += chr(max(0, min(((val>>8)&0xff)-128, 255)))
        string += chr(max(0, min((val&0xff)-128, 255)))
    return string.partition('\x00')[0]

def string_to_ints(in_string, length=8):
    ints = []
    for i in range(length):
        string = ''
        for j in range(i*4, i*4+4):
            if in_string and j < len(in_string):
                string += in_string[j]
            else:
                string += chr(0)
        ints.append(int32(((ord(string[0])+128)<<24)|((ord(string[1])+128)<<16)|((ord(string[2])+128)<<8)|(ord(string[3])+128)))
    ints[-1] &= int32(0xffffff00)
    return ints