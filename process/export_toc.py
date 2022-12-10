import sys
import os
import re
import json

sys.path.append('lib')
sys.path.append('../lib')
import filesystem


dir_source = 'src/'
json_output = '_site/theme/js/toc.json'
menu_path = '_site/theme/js/menu.js'

def clean_title(input):
    output = input.replace('"','').replace("'",'')
    while output.startswith(' '):
        output = output[1:]
    while output.endswith(' '):
        output = output[:-1]
    return output

if __name__=='__main__':

    template_files = filesystem.find_files_in_hierarchy(dir_source, lambda f: f.endswith('.html.j2'))
    toc = []
    for entry in template_files:
        f = entry['dir']+entry['filename']
        title = "unknown"
        with open(f,'r') as fid:
            text = fid.read()
            r_title = r'tocTitle.*?=(.*)%}'
            match = re.findall(r_title, text)
            
            if len(match)==1:
                title = clean_title(match[0])
        
        path = entry['dir'][len(dir_source):]+entry['filename'].replace('.html.j2','.html')
        toc.append({'path':path, 'title':title ,'level':entry['level']})
    
    with open(json_output, 'w') as json_fid:
        json.dump(toc, json_fid, indent=4)

    menu_content = ''
    with open(menu_path, 'r') as menu_fid:
        menu_content = menu_fid.read()
    
    toc_txt = '['
    for k,entry in enumerate(toc):
        to_local = '../'*entry['level']
        toc_txt += '{"path":"'+to_local+entry['path']+'", "title":"'+entry['title']+'", "level":'+str(entry['level'])+'}'
        if k<len(toc)-1:
            toc_txt += ', '
    toc_txt +=']'
        
    menu_content = menu_content.replace('{{TOC}}',toc_txt)
    with open(menu_path, 'w') as menu_fid:
        menu_fid.write(menu_content)

    



