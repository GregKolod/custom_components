import xml.etree.ElementTree as ET

tree = ET.parse('pl.xml')
myroot = tree.getroot()

for element in tree.findall('channel'):
    kanal = element.find('display-name').text
    icon = element.find('icon').attrib['src']
    print(kanal, icon)

for prog in tree.findall('programme'):
    title = prog.find('title').text
    programy = prog.attrib['channel']
    print(title, programy)
