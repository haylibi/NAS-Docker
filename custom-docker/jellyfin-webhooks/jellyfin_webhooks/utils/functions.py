import bs4
import pathlib
from typing import Optional, Union, Dict, Any

def markup_language_to_json(xml_filepath: Optional[Union[str, pathlib.Path]] = None, xml_content: Optional[str] = None) -> Dict[str, Any]:
    if xml_filepath is not None:
        with open(xml_filepath, 'r', encoding='utf-8') as f:
            btree = bs4.BeautifulSoup(f, "xml")
    elif xml_content is not None:
        btree = bs4.BeautifulSoup(xml_content, "xml")
    else:
        return {}
    
    # BeautifulSoup automatically adds a generic <html> tag if not strict, 
    # generally we want the first real child.
    root = btree.find() 
    if not root:
        return {}
        
    return {root.name: _xml_to_json(root)}

def _xml_to_json(tag: Union[bs4.element.Tag, bs4.element.NavigableString]) -> Any:
    # 1. Handle Strings (Text Nodes)
    if isinstance(tag, bs4.element.NavigableString):
        text = tag.strip()
        return text if text else None

    output = {}
    
    # 2. Add Attributes if they exist
    if tag.attrs:
        output['@attributes'] = tag.attrs

    # 3. Iterate over immediate children only
    # We use find_all(recursive=False) or tag.children to avoid flattening the tree
    children = [child for child in tag.children if isinstance(child, (bs4.element.Tag, bs4.element.NavigableString))]
    
    has_only_text = True
    
    for child in children:
        # Skip empty whitespace strings
        if isinstance(child, bs4.element.NavigableString):
            if not child.strip():
                continue
            # If we found actual text, we process it, but usually mixed content is rare in data XMLs
            # We will assign it to a special key '#text' if there are also attributes or other tags
            output['#text'] = child.strip()
            continue
        
        has_only_text = False
        child_data = _xml_to_json(child)
        
        # 4. Handle Lists (Multiple tags with the same name)
        if child.name in output:
            # If item is not a list yet, convert it to a list containing the previous item
            if not isinstance(output[child.name], list):
                output[child.name] = [output[child.name]]
            output[child.name].append(child_data)
        else:
            output[child.name] = child_data

    # 5. Simplify output if it's just text without attributes
    # If the tag had no attributes and only contained text, return just the string
    if not tag.attrs and has_only_text:
        return output.get('#text', '')

    return output
if __name__ == '__main__':

    xml = markup_language_to_json('/mnt/data/media/series/Better Call Saul/Season 3/Better Call Saul (2015) S03E01 (1080p NF WEB-DL DDP5.1 AV1) - Vialle.nfo')
    print('Hey Oh')
