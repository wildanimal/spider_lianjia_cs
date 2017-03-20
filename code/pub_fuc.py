#-*-coding:utf8-*-
import re

def re_fuc(cont,rel_list,id_data):
    for rel in rel_list:
        try:
            # print(rel)
            c = re.compile(rel)
            ret = re.findall(c, cont)
            if ret:
                return ret
            else:
                pass
        except:
            pass

    return []
