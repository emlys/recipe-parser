import argparse
import functools
import multiprocessing
import requests
import subprocess

import pandas
import spacy
from spacy import displacy


DISPLACY_URL = 'http://0.0.0.0:5000'


def show_displacy(doc):
    """
    Visualize a doc with displaCy and show in a firefox tab.

    Args:
        doc (spacy.Doc): document to visualize

    Returns:
        None
    """
    print('Starting displaCy...')
    p = multiprocessing.Process(target=displacy.serve, args=(doc,))
    p.start()

    while True:
        try:
            requests.get(DISPLACY_URL)
            break
        except requests.exceptions.ConnectionError:
            pass

    subprocess.run(['open', '-a', 'firefox', '-g', DISPLACY_URL])
    return p


def edit_until_good(nlp, text):
    doc = nlp(text)
    displacy_process = show_displacy(doc)

    max_i = 8
    max_text = functools.reduce(
        lambda n, t: max(n, len(str(t.text))), doc, 0
    ) + 4

    lines = [f'index   text{" " * (max_text - 4)}pos     tag     head    dep\n']
    for i, token in enumerate(doc):
        lines.append(
            f'{i}{" " * (max_i - len(str(i)))}'
            f'{token.text}{" " * (max_text - len(token.text))}'
            f'{token.pos_}{" " * (max_i - len(token.pos_))}'
            f'{token.tag_}{" " * (max_i - len(token.tag_))}'
            f'{token.head.i}{" " * (max_i - len(str(token.head.i)))}'
            f'{token.dep_}\n')

    whitespace = [bool(token.whitespace_) for token in doc]

    # initialize the file to be edited
    edit_file = 'edit'
    with open(edit_file, 'w') as file:
        file.writelines(lines)

    while True:
        subprocess.run(['subl', 'edit'])

        input('Press Enter when done editing and saving...')
        displacy_process.terminate()

        df = pandas.read_csv(
            'edit', index_col='index', header=0, sep=' +', engine='python')

        new_doc = spacy.tokens.Doc(
            nlp.vocab,
            list(df['text']),
            whitespace,
            pos=list(df['pos']),
            heads=list(df['head']),
            deps=list(df['dep']))

        displacy_process = show_displacy(new_doc)

        done = input('All good? [y/n]')
        if done == 'y':
            displacy_process.terminate()
            docbin = spacy.tokens.DocBin(
                # which attributes to serialize
                attrs=[
                    'ORTH',   # hash of token text
                    'SPACY',  # whether followed by space
                    'TAG',    # fine grained pos tag
                    'POS',    # coarse grained pos tag
                    'HEAD',   # parent in dependency graph
                    'DEP'     # dependency relation to parent
                ],
                docs=[new_doc])
            fulltext = ''.join(
                [token.text_with_ws for token in new_doc]).replace(' ', '_')
            filename = f'{fulltext}.spacy'
            docbin.to_disk(filename)
            break
        else:
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_dir')
    args = parser.parse_args()

    nlp = spacy.load('en_core_web_lg')
    with open(args.input_file) as f:
        for line in f:
            edit_until_good(nlp, line.strip())
