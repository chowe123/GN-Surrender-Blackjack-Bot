import boundingbox
import resource_path

def read_tuples_from_file(filename):
    resource_path.resource_path(filename)
    variables = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue

            # Split into name and tuple string
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()

            # Convert "(983, 310, 1010, 330)" -> tuple of ints
            if value.startswith("(") and value.endswith(")"):
                value = tuple(map(int, value[1:-1].split(",")))
                variables[name] = value

    return variables

def update_var_in_file(var_name, value, filename="Vars.txt"):
    resource_path.resource_path(filename)
    """Update or insert a variable assignment in Vars.txt."""
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(var_name + " "):
            lines[i] = f"{var_name} = {value}\n"
            found = True
            break

    if not found:  # add new variable if not found
        lines.append(f"{var_name} = {value}\n")

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

if __name__ == "__main__":
    filename = "Vars.txt"  # Replace with your file path
    setDealerBbox()
    tuples = read_tuples_from_file(filename)
    for name, value in tuples.items():
        print(f"{name} = {value}")
    