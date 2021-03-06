from pint import UnitRegistry


def get_ms(period_str):
    if type(period_str) is int:
        # If it's set as an integer, assume ms
        return period_str

    ur = UnitRegistry()
    return ur[period_str].to('ms').magnitude


def write(env, input_path, output_path):
    template = env.get_template(str(input_path))
    with open(output_path, 'w') as f:
        f.write(template.render(get_ms=get_ms))
