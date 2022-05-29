#TODO: Find a better method to dynamically set more global variables
#      (ex. https://stackoverflow.com/questions/1429814/how-to-programmatically-set-a-global-module-variable)

import os

# Default model
models_dir = os.path.dirname(os.path.abspath(__file__))
default_model ='default_model.h5'
__default_model__ = os.path.join(models_dir, default_model)

def _check_file_name(name):
    check = True
    for n, char in enumerate(name):
        # first character cannot be a number
        if n == 0:
            check = check and not char.isdigit()
        is_adapted_char = char.isalnum() or char in ['_', '.']
        check = check and is_adapted_char
    return check

def _get_model_name(name):
    new_name = ''
    for char in name:
        if char == '.':
            break
        else:
            new_name += char
    return new_name

# Look for models
files = os.listdir(models_dir)
discard = ['__init__.py', '__pycache__', default_model]
# Remove unimportant files
for file in discard:
    if file in files:
        files.remove(file)
# Add other models
for file in files:
    if _check_file_name(file):
        model_name = _get_model_name(file)
        file = os.path.join(models_dir, file)
        new_model = f'{model_name} = file'
        exec(new_model)