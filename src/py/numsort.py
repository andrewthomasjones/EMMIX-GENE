# numsort.py 
# sorting in numeric order 
# for example:
#   ['aaa35', 'aaa6', 'aaa261'] 
# is sorted into:
#   ['aaa6', 'aaa35', 'aaa261']

import sys

def sorted_copy(alist):
    # inspired by Alex Martelli
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52234
    indices = map(generate_index, alist)
    decorated = zip(indices, alist)
    decorated.sort()
    return [ item for index, item in decorated ]
    
def generate_index(astring):
    """
    Splits a string into alpha and numeric elements, which
    is used as an index for sorting"
    """
    #
    # the index is built progressively
    # using the _append function
    #
    index = []
    def _append(fragment,index=index):
        #  hack: make fragment appear before others
        if fragment.find('groupmeans') >= 0:
            fragment = \
            fragment.replace('groupmeans','GroupMeans')
        # hack: make .cor fragments more expensive
        if fragment.endswith(".cor"):
            index.insert(0,"z")
        if fragment.isdigit(): fragment = int(fragment)
        index.append(fragment)

    # initialize loop
    prev_isdigit = astring[0].isdigit()
    current_fragment = ''
    # group a string into digit and non-digit parts
    for char in astring:
        curr_isdigit = char.isdigit()
        if curr_isdigit == prev_isdigit:
            current_fragment += char
        else:
            _append(current_fragment)
            current_fragment = char
            prev_isdigit = curr_isdigit
    _append(current_fragment)    
    return tuple(index)

    
def _test():
    initial_list = [ '35 Fifth Avenue', '5 Fifth Avenue', '261 Fifth Avenue' ]
    sorted_list = sorted_copy(initial_list)
    import pprint
    print "Before sorting..."
    pprint.pprint (initial_list)
    print "After sorting..."
    pprint.pprint (sorted_list)
    print "Normal python sorting produces..."
    initial_list.sort()
    pprint.pprint (initial_list)

if __name__ == '__main__':
    _test()
