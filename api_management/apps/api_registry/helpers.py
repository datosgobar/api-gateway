def coma_separated_list_of_regex(a_regex):
    return r'^\s*(' + a_regex + ')(,\s*(' + a_regex + '))*\s*$'
