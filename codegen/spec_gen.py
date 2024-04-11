'''
Automated API spec generator. Output stored in api_spec.txt.
'''

import ast

def extract_functions(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()

    tree = ast.parse(source_code)
    functions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)

            # Extract function arguments with their types
            args = []
            for arg in node.args.args:
                arg_type = "Any"
                if arg.annotation:
                    arg_type = extract_type_annotation(source_code, arg.annotation)
                args.append(f"{arg.arg}: {arg_type}")

            # Extract return type
            return_type = "Any"
            if node.returns:
                return_type = extract_type_annotation(source_code, node.returns)

            signature = f"{node.name}({', '.join(args)}) -> {return_type}"
            functions.append((signature, docstring))
    
    return functions

def extract_type_annotation(source_code, node):
    start_line = node.lineno - 1
    end_line = node.end_lineno
    start_col = node.col_offset
    end_col = node.end_col_offset

    # Split the source code into lines
    lines = source_code.split('\n')

    # Extract lines containing the annotation
    annotation_lines = lines[start_line:end_line]

    # If the annotation is on a single line
    if start_line == end_line:
        return annotation_lines[0][start_col:end_col].strip()
    else:
        # If the annotation spans multiple lines, join them together
        annotation_lines[0] = annotation_lines[0][start_col:]
        annotation_lines[-1] = annotation_lines[-1][:end_col]
        return '\n'.join(annotation_lines).strip()


if __name__ == "__main__":
    paths = ['experts/database_experts.py', 'experts/functional_experts.py', 'experts/model_experts.py']
    output_file = 'experts/base_prompt.txt'

    all_functions = []
    for path in paths:
        all_functions.append(extract_functions(path))

    with open(output_file, 'w') as f:
        f.write("API Spec:\n\n")

        for functions in all_functions:
            for signature, docstring in functions:
                f.write(f"{signature}\n")
                f.write(f"{docstring}\n")
                f.write("\n")
    
    print(f"API spec has been written to {output_file}.")