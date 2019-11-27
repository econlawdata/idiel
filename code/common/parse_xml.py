import logging
from collections import namedtuple
from os import chdir
from pathlib import Path

from lxml import etree

if __name__ == '__main__':
    # Update path accordingly. Pointing to the root directory that has folders named 'scrapedb' and 'wtoscrape' which
    # store raw XML files
    path_to_xml_dir = Path('F:/Documents/migrate_db/xml')

    chdir(path_to_xml_dir)

    # Create folders to store processed files
    folder_paths = [Path(name) for name in
                    ('scrapedb_xml_processed', 'wtoscrape_xml_processed', 'scrapedb_txt', 'wtoscrape_txt')]
    for folder_path in folder_paths:
        folder_path.mkdir(exist_ok=True)

    OutputXmlTxtDirs = namedtuple('OutputXmlTxtDirs', ['xml', 'txt'])
    input_output_folders_map = {
        Path('scrapedb'): OutputXmlTxtDirs(Path('scrapedb_xml_processed'), Path('scrapedb_txt')),
        Path('wtoscrape'): OutputXmlTxtDirs(Path('wtoscrape_xml_processed'), Path('wtoscrape_txt')),
    }

    # Start processing
    for input_dir, output_dirs in input_output_folders_map.items():
        for file in input_dir.iterdir():
            print('Processing ' + str(file))
            # Process XML
            try:
                tree = etree.parse(str(file))
            except etree.XMLSyntaxError:
                parser = etree.XMLParser(recover=True)
                tree = etree.parse(str(file), parser)

            root = etree.Element('root')

            for page in tree.getroot().iter():
                # Only proceed when any paragraph presents
                par_nodes = page.findall('p')
                if par_nodes:
                    page_num = page.get('number')
                    page_node = etree.SubElement(root, 'page', number=page_num) if page_num else etree.SubElement(root,
                                                                                                                  'page')
                    for par in par_nodes:
                        # Node for converted paragraph
                        text_nodes = par.findall('text')
                        if text_nodes:
                            # Remove all bold and italic tags first
                            for node in text_nodes:
                                etree.strip_tags(node, 'b', 'i', 'a')
                            # Extract text for each text node and omit the ones without text
                            par_text = ' '.join(filter(lambda text: text, [node.text for node in text_nodes]))
                            etree.SubElement(page_node, 'p').text = par_text

                        # Footnote nodes
                        for footnote_node in par.iter('footnote'):
                            etree.strip_tags(footnote_node, 'b', 'i', 'a')
                            if footnote_node.text:
                                etree.SubElement(page_node, 'footnote').text = footnote_node.text.strip()

            tree_to_write = etree.ElementTree(root)
            tree_to_write.write(str(output_dirs.xml / file.name),
                                pretty_print=True, encoding='utf-8')

            # Get txts
            res = ''

            for page in tree.getroot().iter():
                for par in page.iter('p'):
                    text_nodes = par.findall('text')
                    if text_nodes:
                        # Remove all bold and italic tags first
                        for node in text_nodes:
                            etree.strip_tags(node, 'b', 'i', 'a')
                        # Extract text for each text node and omit the ones without text
                        res += ' '.join(filter(lambda text: text, [node.text for node in text_nodes]))
                        res += '\n\n'

            (output_dirs.txt / file.with_suffix('.txt').name).write_text(res, encoding='utf-8')
