import collections
import json
import sys


TERMINATORS = {"jmp", "br", "ret"}


def construct_basic_blocks(function_dict):
    basic_blocks = []
    current_block = []
    # Assuming there is only "main" function.
    for instruction in function_dict["instrs"]:
        if "op" not in instruction:
            # It's a label. Terminate current block if it exists and start a new block.
            if current_block:
                basic_blocks.append(current_block)
            current_block = [instruction]
        else:
            current_block.append(instruction)
            if instruction["op"] in TERMINATORS:
                basic_blocks.append(current_block)
                current_block = []

    basic_blocks.append(current_block)
    return basic_blocks


def construct_label_to_block_index(basic_blocks):
    label_to_block_index = {}
    for idx, block in enumerate(basic_blocks):
        if "label" in block[0]:
            label_to_block_index[block[0]["label"]] = idx

    return label_to_block_index


def construct_control_flow_graph(basic_blocks):
    graph = collections.defaultdict(list)
    construct_label_to_block_index(basic_blocks)
    label_to_block_index = construct_label_to_block_index(basic_blocks)
    for idx, block in enumerate(basic_blocks):
        last_instruction = block[-1]
        if last_instruction["op"] in {"jmp", "br"}:
            # Identify blocks with labels.
            for label in last_instruction["labels"]:
                graph[idx].append(label_to_block_index[label])
        elif last_instruction["op"] == "ret":
            graph[idx] = []
        elif idx < len(basic_blocks) - 1:
            # The next block has an edge from the current block.
            graph[idx].append(idx + 1)

    return graph


def count_labels(basic_blocks):
    nlabels = 0
    for block in basic_blocks:
        for instr in block:
            if "label" in instr:
               nlabels += 1

    return nlabels 


if __name__ == "__main__":
    program = json.load(sys.stdin)
    for function in program["functions"]:
        basic_blocks = construct_basic_blocks(function)
        control_flow_graph = construct_control_flow_graph(basic_blocks)
        print("Number of labels in {0}: {1}".format(function["name"], count_labels(basic_blocks)))
