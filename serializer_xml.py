import xml.etree.ElementTree as etree
from xml.dom import minidom
import metadata


def write_xml(data, file):
    root = etree.Element('MetaDataObject')
    c = etree.SubElement(root, 'Configuration', {'uid': data.uid})
    collection = etree.SubElement(c, 'InternalInfo')
    for item in data.internalInfo:
        __write_xml(collection, item)
    collection = etree.SubElement(c, 'Properties')
    for prop in data.properties.items():
        val = prop[1]
        if hasattr(val, 'to_xml'):
            val.to_xml(etree.SubElement(collection, prop[0]))
        else:
            etree.SubElement(collection, prop[0]).text = str((prop[1] if prop[1] else ''))
    # etree.ElementTree(root).write('out.xml')
    xmlstr = minidom.parseString(etree.tostring(root)).toprettyxml(encoding='UTF-8')
    with open("out.xml", "wb") as f:
        f.write(xmlstr)


def __write_xml(parent, prop):
    attrs = {}
    if prop.uid is not None:
        attrs['uid'] = prop.uid
    el = etree.SubElement(parent, 'container', attrs)
    for item in prop:
        if isinstance(item, metadata.Properties):
            __write_xml(el, item)
        else:
            etree.SubElement(el, 'data', {'value': item})

