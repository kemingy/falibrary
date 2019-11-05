"""
utils functions
"""
import re
from falcon.routing.compiled import _FIELD_PATTERN

from falibrary.route import _doc_class_name

# NOTE from `falcon.routing.compiled.CompiledRouterNode`
ESCAPE = r'[\.\(\)\[\]\?\$\*\+\^\|]'
ESCAPE_TO = r'\\\g<0>'
EXTRACT = r'{\2}'
# NOTE this regex is copied from werkzeug.routing._converter_args_re and
# modified to support only int args
INT_ARGS = re.compile(r'''
    ((?P<name>\w+)\s*=\s*)?
    (?P<value>\d+)\s*
''', re.VERBOSE)
INT_ARGS_NAMES = ('num_digits', 'min', 'max')


def find_routes(root):
    routes = []

    def find_node(node):
        if node.resource and node.resource.__class__.__name__ not in _doc_class_name:
            routes.append(node)

        for child in node.children:
            find_node(child)

    for route in root:
        find_node(route)

    return routes


def parse_path(path):
    subs, parameters = [], []
    for segment in path.strip('/').split('/'):
        matches = _FIELD_PATTERN.finditer(segment)
        if not matches:
            subs.append(segment)
            continue

        escaped = re.sub(ESCAPE, ESCAPE_TO, segment)
        subs.append(_FIELD_PATTERN.sub(EXTRACT, escaped))

        for field in matches:
            variable, converter, argstr = [field.group(name) for name in
                                           ('fname', 'cname', 'argstr')]

            if converter == 'int':
                if argstr is None:
                    argstr = ''

                arg_values = [None, None, None]
                for index, field in enumerate(INT_ARGS.finditer(argstr)):
                    name, value = field.group('name'), field.group('value')
                    if name:
                        index = INT_ARGS_NAMES.index(name)
                    arg_values[index] = value

                num_digits, minumum, maximum = arg_values
                schema = {
                    'type': 'integer',
                    'format': f'int{num_digits}' if num_digits else 'int32',
                }
                if minumum:
                    schema['minimum'] = minumum
                if maximum:
                    schema['maximum'] = maximum
            elif converter == 'uuid':
                schema = {
                    'type': 'string',
                    'format': 'uuid'
                }
            elif converter == 'dt':
                schema = {
                    'type': 'string',
                    'format': 'date-time',
                }
            else:
                # no converter specified or customized converters
                schema = {'type': 'string'}

            parameters.append({
                'name': variable,
                'in': 'path',
                'required': True,
                'schema': schema,
            })

    return f'/{"/".join(subs)}', parameters
