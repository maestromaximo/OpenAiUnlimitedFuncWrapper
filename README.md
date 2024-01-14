![PyPI](https://img.shields.io/pypi/v/your-package-name.svg)
![License](https://img.shields.io/github/license/maestromaximo/OpenAiUnlimitedFuncWrapper.svg)
# OpenAI Unlimited Function Wrapper

The `openaiunlimitedfuncwrapper` is a Python package that simplifies interaction with the OpenAI API, providing easy access to various models of GPT, including conversational capabilities, dynamic function calling, and pseudo-function execution to elicit specific responses based on parameter modification.

## Features

- Single-question querying to any GPT model and receiving a response.
- Engaging in a conversation with context management.
- Dynamically adding callable functions within the code.
- Forcing execution of real or pseudo-functions to steer responses.
- Automatic and manual creation of JSON schemas for function descriptions.
- Setting the OpenAI API key via code for environment preparation.

## Installation

To install `openaiunlimitedfuncwrapper`, simply run:

```
pip install openaiunlimitedfun
```

## Setting Up Your OpenAI API Key

Before you start using the package, you need to set your OpenAI API key. You can do this by running:

```
from openaiunlimitedfun import set_openai_api_key

set_openai_api_key('your-api-key-here')
```

This will create or append to a `.env` file in your current directory, storing your API key.

## Managing Available Functions

To make custom functions available for the OpenAI API to call during a conversation, use the `manage_available_functions` function:

```
from openaiunlimitedfun import manage_available_functions

# To save current module's functions
manage_available_functions(retrieve=False)

# To retrieve available functions
functions = manage_available_functions()
```

## Adding Functions to the Function List

If you want to add specific functions to be accessible during the conversation, use `manage_function_list`:

```
from openaiunlimitedfun import manage_function_list

# To add a function to the list
manage_function_list(function_to_add='your_function_name')

# To retrieve the list of functions
function_list = manage_function_list(retrieve=True)
```

###
 - After running the above, ```chat_context_function_bank``` will have the functions availible to run

## Generating JSON Schemas for Functions

You can create JSON schemas for your functions automatically or manually. This can be used to generate function descriptions for use within the wrapper.

### Automatic JSON Schema Generation

Automatically generate a JSON schema based on user input:

```
from openaiunlimitedfun import create_json_autoagent

schema = create_json_autoagent('Describe a function that calculates the sum of two numbers.')
print(schema)
```

### Manual JSON Schema Creation

Manually create a JSON schema through an interactive prompt:

```
from openaiunlimitedfun import create_function_json_manual

create_function_json_manual()
# Follow the interactive prompts to create your function JSON schema.
```

## Usage Examples

### Single Question

Query a single question and get a response:

```
from openaiunlimitedfun import single_question

response = single_question("What is the capital of France?")
print(response)
```

### Conversational Context

Engage in a conversation with the ability to maintain context:

```
from openaiunlimitedfun import chat_context_function_bank

question = "Who wrote the play Hamlet?"
context = []  # This should be a list of previous messages if you have them

response, updated_context = chat_context_function_bank(question, context)
print(response)
```

### Pseudo-Function Execution

Force the execution of a pseudo-function to get a desired response:

```
from openaiunlimitedfun import single_turn_pseudofunction

# Define a pseudo-function
pseudo_function = {
    "name": "calculate_sum",
    "parameters": {
        "number1": 5,
        "number2": 3
    }
}

# Use the pseudo-function in a prompt
response = single_turn_pseudofunction("What is the sum of the numbers?", pseudo_function)
print(response)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, and suggest features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

#### Build

- If you want to run a new pip build make sure to actiavte an enviroment, run pip install -r requirement.txt
- Then be sure to run ```Remove-Item -Recurse -Force build, dist, *.egg-info``` if you had run a build before, else it would return an error
- Then run python ```setup.py sdist bdist_wheel```
- If wanted you can then run a pip of the wheel file path ".whl" under the dist folder that was just created 

