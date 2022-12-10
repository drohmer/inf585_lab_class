import sys
import os
import re
import json

sys.path.append('lib')
sys.path.append('../lib')
import filesystem


dir_source = 'src/'
redirection_path = '_site/index.html'

def create_html_redirection(url):
    html = f'''
<html> 
    <head> 
        <meta http-equiv="refresh" content="0; url={url}" /> 
    </head> 
    <body> 
        Redirection to <a href="{url}">{url}</a> 
    </body> 
</html> 
'''

    return html

if __name__=='__main__':

    template_files = filesystem.find_files_in_hierarchy(dir_source, lambda f: f.endswith('.html.j2'))
    first_file = template_files[0]
    
    url = first_file['dir'][len(dir_source):]+first_file['filename'].replace('.html.j2','.html')
    html = create_html_redirection(url)

    with open(redirection_path,'w') as fid:
        fid.write(html)

    



