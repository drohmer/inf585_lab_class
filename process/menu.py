import sys
import os
import re
import json
import yaml

sys.path.append('lib')
sys.path.append('../lib')
import filesystem


menu_path_relative = '/theme/js/menu.js'

def clean_title(input):
    output = input.replace('"','').replace("'",'')
    while output.startswith(' '):
        output = output[1:]
    while output.endswith(' '):
        output = output[:-1]
    return output

def post_process(meta):

    menu_path = meta['dir_site']+menu_path_relative

    # load structure
    structure_path = meta['dir_site']+'/structure/structure.yaml'
    with open(structure_path) as fid:
        structure = yaml.load(fid, Loader=yaml.loader.SafeLoader)
    
    toc_txt = '['
    for k,entry in enumerate(structure):
        to_local = '../'*entry['level']
        toc_txt += '{"path":"'+to_local+entry['dir']+entry['filename']+'", "title":"'+entry['title']+'", "level":'+str(entry['level'])+'}'
        if k<len(structure)-1:
            toc_txt += ', '
    toc_txt +=']'

    menu_content = ''
    with open(menu_path, 'r') as menu_fid:
        menu_content = menu_fid.read()
    menu_content = menu_content.replace('{{TOC}}',toc_txt)
    with open(menu_path, 'w') as menu_fid:
        menu_fid.write(menu_content)

