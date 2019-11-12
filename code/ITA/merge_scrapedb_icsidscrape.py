import re
from os import chdir
from pathlib import Path

import pandas as pd


# Functions get_icsid_prefixes_in_dispute_titles and get_icsid_prefixes_in_icsidscrape
# are for finding malformed ICSID Case No. in dispute titles

def get_icsid_prefixes_in_dispute_titles(titles):
    # List possible prefixes for ICSID Case No. in scrapedb.dispute
    title_prefix = set()
    unmatched_titles_ = []
    for title in titles:
        m = re.search(r'Case No\.\s(.+?)/', title)
        if m:
            title_prefix.add(m.group(1))
        else:
            unmatched_titles_.append(title)

    return sorted(title_prefix), unmatched_titles_


def get_icsid_prefixes_in_icsidscrape(casenos_):
    case_prefix = set()
    for caseno in casenos_:
        case_prefix.add(caseno.split('/')[0])
    return sorted(case_prefix)


def extract_icsid_caseno_from_dispute_titles(titles):
    """
    Extract ICSID Case No. from titles
    :param titles: title column in DataFrame for disputes
    :return: A list of caseno's and unmatched titles. The list will be inserted as a new column in DataFrame for disputes
    """
    rules = {
        'ARB (AF)': 'ARB(AF)',
        'ARB 09': 'ARB/09',
        'ARB 12': 'ARB/12',
        'ARB(AF)04': 'ARB(AF)/04',
        'Arb': 'ARB',
        'Conco': 'CONC',
        'ARB/04/01': 'ARB/04/1',
        'CONC/07/01': 'CONC/07/1',
        'ARB/05/07': 'ARB/05/7',
        'ARB/15/21)': 'ARB/15/21',
        'ARB(AF)/07/01': 'ARB(AF)/07/1',
        'ARB/03/08': 'ARB/03/8'
    }

    unmatched_titles_ = []
    casenos = []

    for title in titles:
        m = re.search(r'Case No\.\s(.+)', title)
        if m:
            caseno = m.group(1)
            for from_substring, to_substring in rules.items():
                caseno = caseno.replace(from_substring, to_substring)
            # After substitutions with rules, there sometimes are comments in brackets
            # We remove it by taking the substring before '\xa0(' (note it is not a normal space)
            caseno = caseno.replace('\xa0', ' ').split(' (')[0]
            if 'formerly' in caseno:
                print(caseno)
            casenos.append(caseno)
        else:
            unmatched_titles_.append(title)
            casenos.append(None)

    return casenos, unmatched_titles_


def merge_dispute_icsid_cases(disputes_, icsid_cases_):
    """
    Merge scrapedb.dispute and icsidscrape.case by extracted ICSID Case No.
    :param disputes_: DataFrame for disputes
    :param icsid_cases_: DataFrame for icsid_cases
    :return: merged DataFrame with essential columns
    """
    dispute_id_icsid_caseno = disputes_.loc[:, ['DISPUTE.id', 'DISPUTE.icsid_caseno']]
    return pd.merge(icsid_cases_, dispute_id_icsid_caseno,
                    how='outer',
                    left_on='ICSID.caseno',
                    right_on='DISPUTE.icsid_caseno')


def get_unmatched_caseno(caseno_case_id_dispute_id):
    """
    From the merged table, find those caseno without a matched dispute
    :param caseno_case_id_dispute_id: Merged DataFrame
    :return: A list of unmatched caseno
    """
    df = caseno_case_id_dispute_id
    return sorted(set(list(df[df['DISPUTE.id'].isna()]['ICSID.caseno'])))


if __name__ == "__main__":
    # If failed, please change the dir accordingly
    chdir('../../ITA/metadata')

    icsid_cases = pd.read_csv('case_full_icsidscrape.csv').rename(columns=lambda col: 'ICSID.' + col)
    disputes = pd.read_csv('dispute_full_scrapedb.csv').rename(columns=lambda col: 'DISPUTE.' + col)

    caseno_prefixes_in_dispute, unmatched_titles = get_icsid_prefixes_in_dispute_titles(disputes['DISPUTE.title'])
    caseno_prefixes_in_icsidscrape = get_icsid_prefixes_in_icsidscrape(icsid_cases['ICSID.caseno'])

    print('Dispute titles with no Case No.:\n' + '\n'.join(unmatched_titles))
    print('\nICSID Case No. prefixes in scrapedb.dispute:', caseno_prefixes_in_dispute)
    print('ICSID Case No. prefixes in icsidscrape.case:', caseno_prefixes_in_icsidscrape)

    # OUTPUTS - 2019-11-06
    # If you see different lists, update rules in extract_icsid_caseno_from_dispute_titles accordingly
    '''
    Dispute titles with no Case No.:
    Agility for Public Warehousing Company K.S.C. v. Republic of Iraq, ICSID
    Windoor v. Republic of Kazakhstan, ICSID
    Deutsche Telekom v. India, ICSID
    
    ICSID Case No. prefixes in scrapedb.dispute: ['ADHOC', 'ARB', 'ARB (AF)', 'ARB 09', 'ARB 12', 'ARB(AF)', 'ARB(AF)04', 'Arb', 'CONC', 'Conco', 'UNCT']
    ICSID Case No. prefixes in icsidscrape.case: ['ADHOC', 'ARB', 'ARB(AF)', 'CONC', 'CONC(AF)', 'UNCT']
    '''
    # END OF OUTPUTS

    casenos_in_dispute_titles, unmatched_titles_in_caseno_extraction = extract_icsid_caseno_from_dispute_titles(
        disputes['DISPUTE.title'])
    disputes['DISPUTE.icsid_caseno'] = casenos_in_dispute_titles

    print('\nUnmatched titles during extraction of Case No. in dispute titles:\n' +
          '\n'.join(unmatched_titles_in_caseno_extraction))

    # Create a dir to store intermediate tables for reference
    Path('intermediate').mkdir(exist_ok=True)

    # Intermediate table for ICSID Case No. extracted from dispute titles
    print('\nSaving dispute titles with extracted ICSID Case No.')
    disputes.to_csv('intermediate/dispute_title_with_icsid_caseno.csv', index=None)

    # Intermediate table for IDs and Case No.s in dispute and icsid
    print('Merging IDs in scrapedb.dispute and icsidscrape.case')
    merged_id_df = merge_dispute_icsid_cases(disputes, icsid_cases)
    merged_id_df.to_csv('intermediate/merged_id_dispute_icsid.csv',
                        columns=['ICSID.caseno', 'DISPUTE.icsid_caseno', 'ICSID.id', 'DISPUTE.id'],
                        index=None)

    print('\nCase No. without matched dispute:\n' + '\n'.join(get_unmatched_caseno(merged_id_df)))

    # Final table
    merged_full_df = pd.merge(disputes, icsid_cases,
                              how='left',
                              left_on='DISPUTE.icsid_caseno',
                              right_on='ICSID.caseno').drop(columns='DISPUTE.icsid_caseno')
    merged_full_df.to_csv('merged_dispute_icsid.csv', index=None)

