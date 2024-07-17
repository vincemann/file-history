

# give me a list like this:
# input_list = ['a', ['b', 'c'], ['d', ['e', 'f', ['g', 'h']], 'i'], 'j', [['k', 'l'], 'm', 'n']]
# and I return a flat list of string-lists with depth=2 [['a'], ['b', 'c'], ['d'], ['e', 'f']...]
def flatten_strings_list(input_element):
    string_lists = []

    def recursive_extraction(element):
        if isinstance(element, list):
            for item in element:
                recursive_extraction(item)
        else:
            string_lists.append([element])

    def extract_string_lists(element):
        if isinstance(element, list):
            if all(isinstance(item, str) for item in element):
                string_lists.append(element)
            else:
                for item in element:
                    extract_string_lists(item)
        else:
            string_lists.append([element])

    extract_string_lists(input_element)
    return string_lists
