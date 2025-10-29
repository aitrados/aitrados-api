


def get_value_by_dict_path(data, path,default_value=None,split_str='.'):
    '''
    a = {'node1': {'node2': [{'node3': 'value1'},{'node3': 'value2'}]}}
path = "node1.node2.1.node3"
value = get_value_by_path(a, path)
print(value) # value2

    '''
    keys = path.split(split_str)
    current = data
    for key in keys:
        try:
            if str.startswith(key,"[") and str.endswith(key,"]"):
                key=int(key[1:-1])

            current = current[key]
            pass
        except (KeyError, TypeError):
            return default_value  # 处理键不存在或类型错误的情况
        except :
            return default_value  # 处理键不存在或类型错误的情况
    return current