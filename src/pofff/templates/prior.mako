{
%for para in dic["hm"]:
"${para}": <${para}>${'' if loop.last else ','}
%endfor
}