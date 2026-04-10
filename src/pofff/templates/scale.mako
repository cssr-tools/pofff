#!/usr/bin/env python

import json

def scale_evaluation():
    """
    Scale transformation
    """
    with open("para.json", "r", encoding="utf8") as file:
        coef = json.load(file)
    para = "{"
% for para in dic["hm"]:
<% lo, hi, scale = dic['hm'][f'{para}'][1], dic['hm'][f'{para}'][2], dic['hm'][f'{para}'][3]%>\
    para += f""""${para}":"""
    para += f"{${lo}+coef['${para}']*(${hi}-${lo})/(1.0*${scale})}${'' if loop.last else ','}"
% endfor
    para += "}"
    with open("parameters.json", "w", encoding="utf8") as file:
        file.write("".join(para))

if __name__ == "__main__":
    scale_evaluation()
