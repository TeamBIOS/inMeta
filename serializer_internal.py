import metadata
import xml.etree.ElementTree as etree
import os


def read_file(file_name):

    obj = []
    levels = []
    level = -1
    word = ''
    with open(file_name, 'r', encoding='utf-8-sig') as f:
        for line in f:
            for c in line[:-1]:
                if c in ',{}':
                    if word != '':
                        # if len(levels[level]) == 0 and word.isdigit():
                        #     pass
                        # else:
                        levels[level].append(word)
                    if c == ',':
                        pass
                    elif c == '{':
                        if level == -1:
                            item = obj
                        else:
                            item = []
                            levels[level].append(item)
                        levels.append(item)
                        level += 1
                    elif c == '}':
                        del levels[level]
                        level -= 1
                    word = ''
                else:
                    word += c
    return obj


def parse(values):
    if isinstance(values, list):
        return parse_prop(values)
    else:
        return values.strip('"')


def isguid(string):
    return len(string) == 36 and \
           string[8] == '-' and \
           string[13] == '-' \
           and string[18] == '-' \
           and string[23] == '-'


def parse_prop(values):
    prop = metadata.Properties()
    offset = -1
    count = 0

    if isinstance(values[0], list):
        pass
    elif values[0].isdigit():
        count = int(values[0])
        offset = 1
    elif len(values) > 1:
        if isguid(values[0]):
            prop.uid = values[0]
            offset = 1
        if isinstance(values[1], str) and values[1].isdigit():
            offset = 2
            count = int(values[1])

    if offset == -1:
        offset = 0
    if count == 0:
        count = len(values) - offset
    if offset != -1:
        while offset < len(values):
            if len(values) < offset + count:
                print('atat')
                count = len(values) - offset
            for i in range(offset, offset + count):
                prop.append(parse(values[i]))
            offset += count
            count = len(values) - offset
    return prop


def get_property(prop, info):
    if info['path'] is None or info['path'] == '':
        return None
    current = prop
    for el in info['path'].split('.'):
        if el.isdigit():
            current = current[int(el)]
    if info['conv_fn']:
        return info['conv_fn'](current, info)
    else:
        return current


def parse_array(values, containers):
    obj = metadata.Configuration()
    obj.uid = values[1][0]

    count = int(values[2])
    for i in range(3, 3 + count):
        value = parse(values[i])
        if value.uid in containers:
            container = containers[value.uid]
            for item in container:
                obj.properties[item['name']] = get_property(value, item)
        obj.internalInfo.append(value)
    return obj


Conversion_fn = {
    'string': lambda x, info: str(x),
    'ml_string': lambda x, info: metadata.MultiLangString.from_array(x),
    'enum': lambda x, info: info['values'][x],
    'bool': lambda x, info: bool(x)
}


def load_config():
    global cfg
    cfg = {}
    tree = etree.parse(os.path.join(os.path.dirname(__file__), 'config.xml'))
    for el in tree.getiterator('MetaDataObject'):
        containers = {}
        name = el.attrib['name']
        if name:
            cfg[name] = containers
            for cont_el in el.getiterator('Container'):
                container = []
                containers[cont_el.attrib['uid']] = container
                for item_el in cont_el.getiterator('item'):
                    container.append({
                        'name': item_el.attrib['value'],
                        'path': item_el.attrib['path'],
                        'type': item_el.attrib['type'],
                        'conv_fn': Conversion_fn[item_el.attrib['type']],
                        'values': {
                            val_el.attrib['key']: val_el.text for val_el in item_el.getiterator('value')
                        }
                    })

cfg = None
