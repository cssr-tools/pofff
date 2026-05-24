#!/usr/bin/env python

import json

def scale_evaluation():
    """Scale transformation"""
    with open("para.json", "r", encoding="utf8") as file:
        coef = json.load(file)
    para = "{"
${para_block}
    para += "}"
    with open("parameters.json", "w", encoding="utf8") as file:
        file.write("".join(para))

if __name__ == "__main__":
    scale_evaluation()
