"""
Generate Can_Libary.c file.
Run this file (with the spec path as a command line argument) to write just
Can_Libary.c or main.py to write all files.
"""
import sys
sys.path.append("ParseCAN")
import ParseCAN
from math import ceil, floor, log2
from common import can_lib_c_path, can_lib_c_base_path


def write(output_path, spec_path, base_path):
    """
    Generate Can_Libary.c file.

    :param output_path: file to be written to
    :param spec_path: CAN spec path
    :param base_path: File with template code that's not autogenerated
    """
    car = ParseCAN.spec.car(spec_path)
    with open(output_path, 'w') as f:
        f.write('#include "Can_Library.h"\n')

        # Copy over base
        with open(base_path) as base:
            lines = base.readlines()
            f.writelines(lines)
        f.write("\n")

        # Write init functions
        for board in car.boards.values():
            if board.arch:  # Means it's a board we program
                for bus_name, bus in board.subscribe.items():
                    f.write("void " + bus_name.title() + "_" + board.name.title() +
                            "_Init(uint32_t baudrate) {\n")
                    f.write("  Can_Init(baudrate);\n")

                    max_id = max(message.can_id for message in bus.messages)

                    # Find mask
                    # The way hardware filtering works is that incoming IDs are
                    # ANDed with the mask and then compared with a preset ID
                    # The goal of this mask is to throw away most higher ID (i.e.,
                    # lower priority) messages
                    mask = 2**(floor(log2(max_id)) + 1) - 1
                    # On a standard bus, IDs are 11 bit
                    max_possible_id = 2**11-1
                    if car.buses[bus_name].is_extended:
                        # On an extended bus, IDs are 29 bit
                        max_possible_id = 2**29-1
                    mask = mask ^ max_possible_id

                    # Set mask (pass in binary to make file more readable)
                    f.write("  Can_SetFilter(" + bin(mask) + ", 0);\n")

                    # Finish up
                    f.write("}\n\n")

                # We still need to create init functions for boards that publish
                # on a bus but don't subscribe
                # Filtering doesn't matter here
                for bus_name, bus in board.publish.items():
                    if bus_name not in board.subscribe.keys():
                        f.write("void " + bus_name.title() + "_" + board.name.title() +
                                "_Init(uint32_t baudrate) {\n")
                        f.write("  Can_Init(baudrate);\n")
                        f.write("}\n\n")

        # Write switch statement
        f.write("""Can_MsgID_T Can_MsgType(void) {
  lastError = Can_RawRead(&lastMessage);
  if (lastError == Can_Error_NO_RX) {
    return Can_No_Msg;
  } else if (lastError != Can_Error_NONE) {
    return Can_Error_Msg;
  }

  uint32_t id = lastMessage.id;

  switch(id) {
""")
        for bus in car.buses.values():
            for message in bus.messages:
                f.write(
                    "    case " + message.name.upper() + "__id:\n" +
                    "      return Can_" + message.name + "_Msg;\n")

        f.write(
            "    default:\n" +
            "      return Can_Unknown_Msg;\n" +
            "   }\n" +
            "}\n\n")

        for bus in car.buses.values():
            for message in bus.messages:

                # Write TO_CAN
                f.write(
                    "TO_CAN(Can_" + message.name + ") {\n" +
                    "  uint64_t bitstring = 0;\n")

                length = 0
                for segment in message.segments:
                    if not message.is_big_endian and (segment.c_type.startswith("int") or
                                                      segment.c_type.startswith("uint")):
                        f.write(
                            "  " + segment.c_type + " " + segment.name + "_swap_value = swap_" + segment.c_type[:-2] +
                            "(type_in->" + segment.name + ");\n" + "  bitstring = INSERT(" + segment.name +
                            "_swap_value, bitstring, " + str(segment.position) + ", " + str(segment.length) + ");\n\n")
                    else:
                        f.write(
                            "  bitstring = INSERT(type_in->" + segment.name + ", bitstring, " + str(segment.position) +
                            ", " + str(segment.length) + ");\n")

                    length += segment.length
                f.write(
                    "  from_bitstring(&bitstring, can_out->data);\n" +
                    "  can_out->id = " + message.name.upper() + "__id;\n" +
                    "  can_out->len = " + str(ceil(length / 8)) + ";\n" +
                    "}\n\n")

                # Write FROM_CAN
                f.write(
                    "FROM_CAN(Can_" + message.name + ") {\n" +
                    "  uint64_t bitstring = 0;\n" +
                    "  to_bitstring(can_in->data, &bitstring);\n")
                for segment in message.segments:
                    if segment.c_type == "enum":
                        enum_name = "Can_" + message.name + "ID_T"

                        f.write(
                            "  type_out->" + segment.name + " = (" + enum_name + ")EXTRACT(bitstring, " +
                            str(segment.position) + ", " + str(segment.length) + ");\n")
                    elif segment.c_type == "bool":
                        f.write(
                            "  type_out->" + segment.name + " = EXTRACT(bitstring, " + str(segment.position) + ", " +
                            str(segment.length) + ");\n")
                    else:
                        if not message.is_big_endian:
                            if segment.signed:
                                f.write(
                                    "  " + segment.c_type + " " + segment.name + "_swap_value=(swap_" +
                                    segment.c_type[:-2] + "(EXTRACT(bitstring, " + str(segment.position) + ", " +
                                    str(segment.length) + ")));\n")
                            else:
                                f.write(
                                    "  " + segment.c_type + " " + segment.name + "_swap_value=swap_u" +
                                    segment.c_type[:-2] + "(EXTRACT(bitstring, " + str(segment.position) + ", " +
                                    str(segment.length) + ")));\n")
                            f.write("  type_out->" + segment.name + " = " + segment.name + "_swap_value;\n")
                        else:
                            if segment.signed:
                                f.write(
                                    "  type_out->" + segment.name + " = SIGN(EXTRACT(bitstring, " +
                                    str(segment.position) + ", " + str(segment.length) + "), " +
                                    str(segment.length) + ");\n")
                            else:
                                f.write(
                                        "  type_out->" + segment.name + " = EXTRACT(bitstring, " +
                                        str(segment.position) + ", " + str(segment.length) + ");\n")
                f.write("}\n\n")

        # Write DEFINE statements
        for bus in car.buses.values():
            for message in bus.messages:
                f.write("DEFINE(Can_" + message.name + ")\n")


if __name__ == "__main__":
    spec_path = sys.argv[1]
    write(can_lib_c_path, spec_path, can_lib_c_base_path)
