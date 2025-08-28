import os
import re

file_1 = open(os.path.join(os.getcwd(), 'client\\templates\\client\\content.html'), 'r', encoding="utf8")
file_2 = open(os.path.join(os.getcwd(), 'client\\templates\\client\\content_changed.html'), 'w', encoding="utf8")

for content in file_1:
    content = re.sub('"(assets.*?)"', "\"{% static \'"+r"\1"+"\' %}\"", content)
    file_2.write(content)
    
file_1.close()
file_2.close()