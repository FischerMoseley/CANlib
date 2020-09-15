import sys
sys.path.append('ParseCAN')
import ParseCAN

from common import pack_unpack_c_path


def write(env, output_path=pack_unpack_c_path):
    '''
    Generate pack_unpack.c file.

    :param output_path: file to be written to
    :param can: CAN spec
    :param base_path: File with template code that's not autogenerated
    '''
    template = env.get_template("pack_unpack.c.j2")
    with open(output_path, 'w') as f:
        f.write(template.render())
