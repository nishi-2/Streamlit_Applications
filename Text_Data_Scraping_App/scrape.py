import requests, re
from bs4 import BeautifulSoup, Tag
from collections import defaultdict


def scrape_content(url):
    # performing all operations inside try block to catch expections if any
    # region - Checking the url access status, if success then parsing the content with html parser
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return f"Request Error: Status code {response.status_code}."

        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        #region end



        #region - Scraping the web sequentially, keeping record of the path in the form of tags
        #         Looking for tags with text content and skipping the other form of tags
        content_dict = defaultdict(str) #creating a dictionary with text content

        def traverse_tree(node, path=[]):
            if not node or not node.name:  #if the node is None then loop will continue
                return

            current_path = path + [node.name]  #concatenate the path names
            counter = 0  #keeping a counter to separate out the nested nodes so that we get unique key

            #checking if the node name is div then looping through the child nodes to keep the content of heading and paragraphs
            #for every nested div, p and h. Not considering certain content like follow share etc.
            if node.name in ['div']:
                #if there are no child tags for div then get the direct text content
                if not any(isinstance(c, Tag) for c in node.children):
                    text_content = node.get_text(strip=True)
                    if text_content:
                        path_key = ",".join(current_path)
                        content_dict[path_key] = text_content

                for child in node.children:
                    if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']:
                        #handling text within p tags that may contain nested elements
                        if (child.name == 'p') and any(isinstance(c, Tag) for c in child.children):
                            text_content = parse_nested_p(child)  #new function to help with nested p tags
                        elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            text_content = child.get_text(strip=True).upper()
                        else:
                            text_content = child.get_text(strip=True)
                        
                        if text_content and text_content.lower() not in ['sign up', 'sign in', 'follow', 'share', 'listen']:
                            counter += 1
                            path_key = ",".join(current_path)
                            content_dict[path_key+'_'+str(counter)] = text_content

                    traverse_tree(child, current_path)  #performing recurssion to go through the nested tags

            #checking of other p and heading tags that might not be inside div
            elif node.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']:
                if node.name == 'p' and any(isinstance(c, Tag) for c in node.children):
                    text_content = parse_nested_p(node)
                elif node.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    text_content = node.get_text(strip=True).upper()
                else:
                    text_content = node.get_text(strip=True)

                if text_content and text_content.lower() not in ['sign up', 'sign in', 'follow', 'share', 'listen']:
                    path_key = ",".join(current_path)
                    content_dict[path_key] = text_content

            #for every other tag, we  are not considering the path and the content
            else:
                for child in node.children:
                    traverse_tree(child, current_path)
        #region end


        #region start - function to parse nested tags within p and handling br and a tags
        def parse_nested_p(p_tag):
            result = []
            for child in p_tag.children:
                #insert newline for br tags
                if isinstance(child, Tag):
                    if child.name == 'br':
                        result.append('\n')  
                    else:
                        #handling situations where the child text is the key and the next sibling to the child text has the value
                        #generally handling the strong tag
                        child_text = child.get_text(strip=True)
                        next_text = child.next_sibling.strip() if child.next_sibling and isinstance(child.next_sibling, str) else ''
                        result.append(f"{child_text} {next_text}")

                elif isinstance(child, str) and child.strip():
                    result.append(child.strip())

            return " ".join(result).replace(" \n ", "\n")
        #region end



        traverse_tree(soup) #calling function to start the loop
        result = dict(content_dict) #storing the scraped content
        


        #region - Some values might repeat due to recussion through tags. We will keep the latest tag value
        unique_values = {}

        for key, value in reversed(content_dict.items()): 
            if value not in unique_values:
                unique_values[value] = key  

        result = {unique_values[value]: value for value in reversed(unique_values)}
        #region end




        #region - Creating a modified dictionary that will not consider the tags having only dates
        # And will perform few other operations on display data
        date_pattern = re.compile(r'\b\d{1,2}\s\w+,\s\d{4}\b')
        modified_dict = defaultdict(str)
        prev_h1_key = None  #store the previous key if its an h1

        for key, value in result.items():
            #searching for date in the node value and skipping if any
            if date_pattern.search(value):
                continue 

            #checking if there are two consecutive h1 or h2 then joining both with pipe | and upper case a tag content
            if key.endswith('h1') or key.endswith('h2')  or key.endswith('a'):
                value = value.upper()
                if prev_h1_key:
                    modified_dict[prev_h1_key] += f" | {value}"
                    prev_h1_key = None  #reset previous h1 key
                else:
                    modified_dict[key] = value
                    prev_h1_key = key
            else:
                #add all the other tags in the modified dictionary as it is
                modified_dict[key] = value
        #region end


        result2 = dict(modified_dict)
        return result2 #final result
    
    
    except Exception as e:
        return f"An error occurred: {e}"
    



def get_data(url):
    #returning the complete data by joining all the values with double entry
    final_data = scrape_content(url)
    return '\n\n'.join(list(final_data.values())) if isinstance(final_data, dict) else final_data
