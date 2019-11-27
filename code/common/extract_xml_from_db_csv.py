from os import chdir
from pathlib import Path

import pandas as pd


def create_xml(row):
    with open('{}.xml'.format(row[0]), 'w') as f:
        f.write(row[1])


if __name__ == '__main__':
    root_dir = Path('F:/Documents/migrate_db/xml')
    root_dir.mkdir(exist_ok=True)
    chdir(root_dir)
    Path('scrapedb').mkdir(exist_ok=True)
    Path('wtoscrape').mkdir(exist_ok=True)

    scrapedb_xml_df = pd.read_csv('scrapedb_xml.csv')
    wtoscrape_xml_df = pd.read_csv('wtoscrape_xml.csv')

    chdir('scrapedb')
    scrapedb_xml_df.apply(create_xml, axis=1)

    chdir('../wtoscrape')
    wtoscrape_xml_df.apply(create_xml, axis=1)
