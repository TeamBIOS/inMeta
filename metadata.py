import xml.etree.ElementTree as etree


class Serializable:

    def to_xml(self):
        pass


class MultiLangString(dict, Serializable):

    def to_xml(self, parent):
        for val in self.items():
            item = etree.SubElement(parent, 'item')
            etree.SubElement(item, 'lang').text = val[0]
            etree.SubElement(item, 'content').text = val[1]

    @staticmethod
    def from_array(values):
        val = MultiLangString()
        for i in range(0, len(values), 2):
            val[values[i].strip('"')] = values[i + 1].strip('"')
        return val


class Properties(list):
    def __init__(self):
        self.uid = None


class MetadataContainer:
    def __init__(self):
        self.uid = None
        self.internalInfo = []


class Configuration(MetadataContainer):
    def __init__(self):
        super(Configuration, self).__init__()
        self.properties = {}
