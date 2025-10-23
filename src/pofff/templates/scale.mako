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
    para += f""""${para}":"""
    para += f"{${dic[f"{para}"][1]}+coef['${para}']*(${dic[f"{para}"][2]}-${dic[f"{para}"][1]})/(1.0*${dic[f"{para}"][3]})}${'' if loop.last else ','}"
% endfor
    para += "}"
    with open("parameters.json", "w", encoding="utf8") as file:
        file.write("".join(para))

if __name__ == "__main__":
    scale_evaluation()
