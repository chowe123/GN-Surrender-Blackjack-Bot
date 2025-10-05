import boundingbox
import resource_path

import ast
import resource_path

def read_tuples_from_file(filename):
    """Read variables (tuples, ints, strings, floats) from a file into a dict."""
    filename = resource_path.resource_path(filename)
    variables = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue

            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()

            try:
                # Safely evaluate literal values: tuple, int, float, str
                parsed_value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                # Fallback: treat as raw string
                parsed_value = value

            variables[name] = parsed_value

    return variables


def update_var_in_file(var_name, value, filename="Vars.txt"):
    """Update or insert a variable assignment in the file."""
    filename = resource_path.resource_path(filename)

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    # Format value for writing
    if isinstance(value, str) and not (value.startswith(("(", "[", "{")) and value.endswith((")", "]", "}"))):
        value_str = f'"{value}"'  # wrap plain strings in quotes
    else:
        value_str = str(value)

    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(var_name + " "):
            lines[i] = f"{var_name} = {value_str}\n"
            found = True
            break

    if not found:
        lines.append(f"{var_name} = {value_str}\n")

    with open(filename, "w") as f:
        f.writelines(lines)




def setDealerBbox():
    global dealer
    print("Select dealer bounding box")
    dealer = boundingbox.pick_bbox()
    print("Dealer bbox set to:", dealer)
    update_var_in_file("dealer", dealer)
    return dealer


def setPlayerTableBbox():
    global playerTable
    print("Select player table bounding box")
    playerTable = boundingbox.pick_bbox()
    print("Player table bbox set to:", playerTable)
    update_var_in_file("playerTable", playerTable)
    return playerTable


def setButtonBbox():
    global buttonBbox
    print("Select button bounding box")
    buttonBbox = boundingbox.pick_bbox()
    print("Button bbox set to:", buttonBbox)
    update_var_in_file("buttonBbox", buttonBbox)
    return buttonBbox

def setSpecificCardBbox():
    global specificCardBbox
    print("Select specific card bounding box")
    specificCardBbox = boundingbox.pick_bbox()
    print("Specific card bbox set to:", specificCardBbox)
    update_var_in_file("specificCard", specificCardBbox)
    return specificCardBbox

if __name__ == "__main__":
    filename = "Vars.txt"  # Replace with your file path
    #setDealerBbox()
    tuples = read_tuples_from_file(filename)
    for name, value in tuples.items():
        print(f"{name} = {value}")
    