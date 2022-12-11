from jinja2 import Environment, FileSystemLoader
# pip3 install Jinja2
# pip3 install jinja-markdown
import sass      #pip3 install libsass
import tidylib   #pip3 install pytidylib
import yaml # pip install pyyaml
import os
import shutil
import argparse
import subprocess
import sys
import re

from lib import filesystem
sys.path.append('lib/lhtml/src/')
import lhtml


meta = {
    'dir_source': 'src/',
    'dir_site': '_site',
    'theme': 'theme_templates/webpage-frame/'
}

def extract_data_from_file(file, regex):
    # Read file
    file_content = ''
    with open(file,'r') as fid:
        file_content = fid.read()
    
    #compile regex
    for r in regex:
        regex_compiled = re.compile(r,  re.DOTALL | re.MULTILINE)
        match = re.findall(regex_compiled, file_content)
        if len(match)>=1:
            data = match[0]
            return data
    
    print('Failed to extract data in file ',file)


def extract_titles(template_files):

    for entry in template_files:
        path = entry['dir']+entry['filename']
        regex = [r'tocTitle.*?=(.*?)%}', r'^(=+) (.*?)$']    
        data = extract_data_from_file(path, regex)
        print(data)

if __name__== '__main__':

    parser = argparse.ArgumentParser(description='Generate VISTA Website.')
    parser.add_argument('-d','--debug', action='store_true',help='Display all lines of the html file when tidyhtml detects a warning or an error.')
    parser.add_argument('-c','--clean', action='store_true',help='Clean the directories.')
    args = parser.parse_args()

    if args.clean==True:
        os.system('rm -rf _site/')
        os.system('rm -rf lib/__pycache__')
        os.system('rm -rf scripts/__pycache__')
        assert(os.path.isdir('_site/')==False)
        print('Directories cleaned')
        exit()
        



    dir_source = meta['dir_source']
    dir_site = meta['dir_site']

    sass_directory = 'theme/css/'


    tidylib.BASE_OPTIONS = {}
    tidyOptions = {'doctype':'html5','warn-proprietary-attributes':'no','show-warnings':'no'}

    # Remove previous site
    print(f'Copy source files {dir_source} to {dir_site}')
    filesystem.copy_directories(dir_source, dir_site)
    print("\t Copy done\n")

    # Copy current theme
    print('Copy current theme',meta['theme'],'into theme/')
    theme_src = meta['theme']
    theme_dst = dir_site+'/theme/'
    filesystem.copy_directories(theme_src, theme_dst)
    print('\t Done\n')


    # Find all html.j2 files
    print(f'Look for jinja template files in {dir_site} ...')
    template_files = filesystem.find_files_in_hierarchy(dir_site, lambda f: f.endswith('.html.j2'))
    print(f'\t Found {len(template_files)} template files\n')

    # Try to find title for each file
    extract_titles(template_files)

    # Export files as yaml stucture for other process
    path_yaml = dir_site+'/files_structure.yaml'
    print(template_files)
    with open(path_yaml,'w') as fid:
        yaml.dump(template_files, fid)


    # Load jinja
    print(f'Load jinja environment on {dir_site}')
    file_loader = FileSystemLoader(dir_site)
    env = Environment(loader=file_loader,extensions=['jinja_markdown.MarkdownExtension'])
    print('\t Jinja environment loaded\n')


    # Convert all jinja files
    print(f'Convert html.j2 files')
    for element in template_files:
        template_path_local = element['dir'][len(dir_site):]+element['filename']
        
        if not template_path_local.find('/templates/')==0: # do not convert base jinja template

            template_path = dir_site+template_path_local
            
            print('\t - ',template_path)
            path_to_root = '../'*element['level']

            # Run Jinja
            template = env.get_template(template_path_local)
            output_html = template.render({'pathToRoot':path_to_root})
            
            # Run LHTML
            output_html = lhtml.run(output_html)

            # Tidy
            tidy_html, error_tidy_html = tidylib.tidy_document(output_html, options=tidyOptions)
            if error_tidy_html!="":
                print("Tidy found error in file "+template_path)
                print(error_tidy_html)
                #debug:
                if args.debug==True:
                    debug = output_html.split('\n')
                    for k,line in enumerate(debug):
                        print(k+1,': ',line)


            # Copy file in output directory
            template_path_output = template_path.replace('.html.j2','.html')
            with open(template_path_output,'w') as fid:
                fid.write(tidy_html)
            
            # Remove template file
            os.remove(template_path)


    # Clean
    print()

    
    


    # Find sass files
    print(f'Look for sass files in {dir_site}{sass_directory} ...')
    sass_files = filesystem.find_files_in_hierarchy(dir_site, lambda f: f.endswith('.sass'))
    print(f'\t Found {len(sass_files)} sass files\n')

    for element in sass_files:
        path_sass = dir_site+element['dir'][len(dir_site):]+element['filename']
        css_txt = sass.compile(filename=path_sass)
        
        # write css file
        path_css_output = path_sass.replace('.sass', '.css')
        with open(path_css_output,'w') as fid:
            fid.write(css_txt)

        # remove sass file
        os.remove(path_sass)



    # Run all process scripts
    dir_process = 'process/'
    all_process = filesystem.find_files_in_hierarchy(dir_process, condition=lambda f: f.endswith('.py'))
    for script in all_process:
        print('Run script '+script['filename'])
        filepath = dir_process + script['filename']
        subprocess.call(['python3',filepath])
