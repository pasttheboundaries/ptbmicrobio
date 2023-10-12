"""
AST stands for antibiotic sensitiviti testing

This package provides means to:
- parse AST results
- test microorganism by applying statistics to AST

basc object is AST which is a dictionary of the following structure:
{
    'abx0': ('1', None)
    'abx1': ('-1', 0.25)
}
where keys are antibiotic names and values are the SensitivityResult
SensitivityResult is a tuple that holds 2 items :
first being the interpretation of resistance (1 for resistant, 0 for intermediate, -1 for sensitive)
second is the mic value

# this instantiates AST
ast = AST()
# in this case AST has no data and items can be added as in a reagular dictionary (dict)
# if this method is used, validity of keys and values will be checked

# alternativelly an AST objact or a valid dict can be given at instantiation
ast = AST(valid_dictionary)
or
ost = AST(other_ast)


# the same can be achieved by using class methods
ast = AST.from_dict()  # this is equivalet to passing a valid dict at instantiation
ast = AST.from_json() # parses json string
ast = AST.parse()  # parses any string - this constructs (finds) a reges patterns that parses the string
    if used multiple times reuses previously found regex patterns for speed.


"""

from .classes import AST, SensitivityReadout
