
import os
import json
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential
from dotenv import load_dotenv, find_dotenv
import pickle
import inspect
import sys
import importlib.util
import openai
from pathlib import Path
# Load environment variables from .env file
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)
load_dotenv(find_dotenv())

def set_openai_api_key(api_key, env_file_path=None):
    """
    Sets the OPENAI_API_KEY in a .env file. Creates the file if it doesn't exist,
    or appends to it if it does. Optionally, a path to a .env file can be provided.

    Args:
        api_key (str): The OpenAI API key to set.
        env_file_path (str, optional): The path to the .env file.
    """
    if env_file_path is None:
        # If no specific path provided, try to find the .env file
        env_file_path = find_dotenv() if find_dotenv() else '.env'
    
    env_path = Path(env_file_path)
    api_key_entry = f'OPENAI_API_KEY={api_key}\n'

    if env_path.exists():
        # Check if OPENAI_API_KEY is already in the file
        with env_path.open('r+') as file:
            lines = file.readlines()
            file.seek(0)
            key_exists = False
            for line in lines:
                # Update the existing API key
                if line.startswith('OPENAI_API_KEY'):
                    file.write(api_key_entry)
                    key_exists = True
                else:
                    file.write(line)
            if not key_exists:
                # Append the API key if it's not in the file
                file.write(api_key_entry)
            file.truncate()  # Remove any trailing lines that were in the original file
    else:
        # Create .env file and write the API key
        with env_path.open('w') as file:
            file.write(api_key_entry)

    print(f"API key set in {env_file_path}.")

def manage_available_functions(retrieve=True, function_location=None):
    """
    Manages the available functions by either retrieving them from a pickle file or saving them to the pickle file.

    Args:
        retrieve (bool, optional): If True, retrieves the available functions from the pickle file. If False, saves the available functions to the pickle file. Defaults to True.
        function_location (str, optional): The path to the module containing the functions. Only used when retrieve is False. Defaults to None.

    Returns:
        dict or None: If retrieve is True, returns a dictionary of available functions. If retrieve is False, returns None.
    """
    pickle_file = 'aiFunctionsPickleAvlbFuncs.pkl'

    if not retrieve:
        if function_location:
            try:
                # Dynamically load the module from the given path
                spec = importlib.util.spec_from_file_location("module.name", function_location)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                print(f"Error loading module from path {function_location}: {e}")
                # Inspect the caller's module in case of error
                module = inspect.getmodule(inspect.currentframe().f_back)
        else:
            # Inspect the caller's module
            module = inspect.getmodule(inspect.currentframe().f_back)

        available_functions = {name: obj for name, obj in inspect.getmembers(module, inspect.isfunction)
                               if inspect.getmodule(obj) == module}

        with open(pickle_file, 'wb') as file:
            pickle.dump(available_functions, file)
        return None

    else:
        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as file:
                available_functions = pickle.load(file)
            return available_functions
        else:
            return {}


def manage_function_list(function_to_add=None, retrieve=True):
    """
    Manages a list of functions stored in a pickle file.

    Args:
        function_to_add: The function to add to the list (default: None).
        retrieve: A boolean indicating whether to retrieve the list (default: True).

    Returns:
        If retrieve is True, returns the list of functions.
        If retrieve is False, returns None.
    """
    pickle_file = "aiFunctionsPicklePkc.pkl"

    # Check if the pickle file exists and load or initialize the function list
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as file:
            functions_list = pickle.load(file)
    else:
        functions_list = []

    # Add a new function to the list if provided
    if function_to_add is not None:
        functions_list.append(function_to_add)
        with open(pickle_file, 'wb') as file:
            pickle.dump(functions_list, file)

    # Return the list if retrieve is True, otherwise return None
    return functions_list if retrieve else None


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_context_function_bank(question, context, model="gpt-3.5-turbo-0613", function_call='auto'):
    """
    Sends a question to the GPT model and executes a function call based on the response.
    The function call is determined by the model's response or by the most relevant function found in the available functions.

    Parameters:
    - question (str): The user's question or input to be sent to the GPT model.
    - context (list, optional): A list of previous messages for context. Defaults to None.
    - model (str, optional): The GPT model to be used. Defaults to "gpt-3.5-turbo-0613".
    - function_call (str, optional): The type of function call to execute. Defaults to 'auto'.

    Returns:
    - str or None: The response from the GPT model or the output of the executed function, or None in case of an error.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    
    messages = [{"role": "user", "content": question}]
    if context:
        temp = context + messages
        messages = temp
        context = messages

    json_data = {"model": model, "messages": messages}
    # print(df)
    functions = manage_function_list(retrieve=True)
    available_functions = manage_available_functions(retrieve=True)
    if functions is not None and not []: ##if functions empty this gives error
        json_data.update({"functions": functions})
    if function_call is not None and functions != []:
        json_data.update({"function_call": function_call})
    # print('FUNCTIONS:', functions)
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
        assistant_message = response.json()["choices"][0]["message"]
        # print('ASSISTANT', assistant_message['content'])
        if assistant_message['content']:
            # print('not none')
            messages.append({"role": "assistant", "content": assistant_message['content']})
        context = messages

        function_responses = []
        if 'function_call' in assistant_message:
            tool_call = assistant_message['function_call']
            function_name = tool_call['name']
            function_args = json.loads(tool_call['arguments'])
            messages.append({
                "role": "assistant",
                "content": assistant_message.get('content'),
                "function_call": assistant_message['function_call']
            })
            context = messages

            if function_name in available_functions:
                function_response = available_functions[function_name](**function_args)
                function_responses.append({
                    "role": "user",
                    "content": f"This is a hidden system message that just shows you what the function returned, answer the previous user message given that this is what it evaluated to, only pay attention to the values not the prompt I am giving you now: {function_response}"
                })
                messages.extend(function_responses)
                context = messages
            else:
                raise ValueError(f"Function {function_name} not defined.")

            if function_responses:
                
                
                follow_up_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json={"model": model, "messages": messages})
                follow_up_message = follow_up_response.json()["choices"][0]["message"]
                messages.append({"role": "assistant", "content": follow_up_message['content']})
                context = messages
                return follow_up_message['content'], context
        else:
            return assistant_message['content'], context

    except Exception as e:
        print(f"Error during conversation: {e}")
        return None, messages



@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def single_question(question, model="gpt-3.5-turbo-0613"):
    """
    Sends a question to the GPT model
    """
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    
    messages = [{"role": "user", "content": question}]
    
    json_data = {"model": model, "messages": messages}
    # print(df)
   
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
        assistant_message = response.json()["choices"][0]["message"]
        # print('ASSISTANT', assistant_message['content'])
        
        

        return assistant_message['content']

    except Exception as e:
        print(f"Error during conversation: {e}")
        return messages
    

def extract_json_from_string(input_string):
    """
    Extracts a JSON string from the input string. The JSON string must be enclosed
    between triple backticks (```json and ```) in the input string.

    Parameters:
    - input_string (str): The string to search for the JSON content.

    Returns:
    - str or None: The extracted JSON string if found, otherwise None.
    """
    # Define the start and end markers for the JSON content
    start_marker = "```json"
    end_marker = "```"

    # Find the start and end positions of the JSON content
    start_pos = input_string.find(start_marker)
    end_pos = input_string.find(end_marker, start_pos + len(start_marker))

    # Check if both markers are found and extract the content if they are
    if start_pos != -1 and end_pos != -1:
        # Add the length of the start marker to start_pos to exclude it from the result
        json_content = input_string[start_pos + len(start_marker):end_pos].strip()
        return json_content

    return None

def create_json_autoagent(message):
    """
    Creates a JSON agent that generates JSON schemas for functions based on user input.

    Args:
        message (str): The user's input message.

    Returns:
        str: The generated JSON schema.

    Raises:
        None
    """
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": """You are an expert at generating JSON schemas for functions. You have a deep understanding of function parameters and their types, and you're skilled in translating these into detailed JSON schemas. Whether given a function definition, like a Python function or a detailed description of its behavior and parameters, you can extract a JSON schema that accurately represents the function.

            Your task is to help users create valid JSON schemas that reflect the structure and requirements of the functions they describe. These schemas should detail the function's name, description, and parameters, including parameter types and whether they are required.

            For example, given a Python function like def test_function(is_testing):, you will generate a JSON schema that captures its essence. Here's an example of how you would represent the test_function in JSON schema:

            json
            Copy code
            {
                "name": "test_function",
                "description": "This is a testing function solely used to test your function calling ability, use it when requested",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_testing": {
                            "type": "boolean",
                            "description": "Set to true when called since you would be testing"
                        }
                    },
                    "required": [
                        "is_testing"
                    ]
                }
            }

            Your role includes aiding in debugging issues with the schemas and providing guidance on modifying them as needed.

            Remember to adhere to the JSON schema standards and best practices, ensuring that the schemas are not only valid but also practical and useful for the users' needs."""},
            {"role": "user", "content": message}
        ]
    )
    responses = completion.choices[0].message.content
    cleaned_json = extract_json_from_string(responses)
    # print(cleaned_json)
    return cleaned_json

def create_function_json_manual():
    """
    Interactively prompts the user to create a JSON schema for a new function. 
    This includes the function's name, description, parameters, and parameter types.

    Returns:
    - dict: A dictionary representing the JSON schema of the newly created function.
    """
    function = {}
    
    function['name'] = input("Enter the function name: ")
    function['description'] = input("Enter the function description: ")

    # Defining parameter types that can be chosen
    available_types = ['string', 'integer', 'boolean']

    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    while True:
        param_name = input("Enter parameter name (or press enter to finish): ")
        if not param_name:
            break

        param_type = ""
        while param_type not in available_types:
            param_type = input(f"Enter parameter type ({'/'.join(available_types)}): ")

        param_desc = input("Enter parameter description: ")

        parameters['properties'][param_name] = {
            "type": param_type,
            "description": param_desc
        }

        if input("Is this parameter required? (yes/no): ").lower() == 'yes':
            parameters['required'].append(param_name)

    function['parameters'] = parameters

    # Printing the function JSON
    print("\nGenerated Function JSON:")
    print(json.dumps(function, indent=4))


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def single_turn_pseudofunction(testing_prompt:str, function:str, model="gpt-4-1106-preview" ):
    """
    Executes a single turn pseudofunction using the OpenAI Chat API.

    Args:
        testing_prompt (str): The user's input or prompt for the conversation.
        function (str): The function to be called as a pseudofunction, doesnt need to exist, its pourpose is to force gpt to respond given the parameters of the function.
        model (str, optional): The model to use for the conversation. Defaults to "gpt-4-1106-preview".

    Returns:
        dict or None: The arguments of the function call if successful {arg: value,...}, None otherwise.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    
    function_call = function['name']

    messages = [{"role": "user", "content": testing_prompt}]
    

    json_data = {"model": model, "messages": messages}
    # print(df)
    functions = [function]
       
    json_data.update({"functions": functions})
    json_data.update({"function_call": {'name': function_call}})
    # print('FUNCTIONS:', functions)
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
        assistant_message = response.json()["choices"][0]["message"]
        # print('ASSISTANT', assistant_message['content'])
      
        if 'function_call' in assistant_message:
            tool_call = assistant_message['function_call']
            function_name = tool_call['name']
            function_args = json.loads(tool_call['arguments'])
            
            # print(function_args)
            return function_args
        else:
            return None

    except Exception as e:
        print(f"Error during conversation: {e}")
        return None
    
#testing func
# func = {
#     "name": "calculate_sum",
#     "description": "This function calculates the sum of two numbers and returns the result.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "number1": {
#                 "type": "number",
#                 "description": "The first number to be added."
#             },
#             "number2": {
#                 "type": "number",
#                 "description": "The second number to be added."
#             }
#         },
#         "required": [
#             "number1",
#             "number2"
#         ]
#     },
#     "return": {
#         "type": "number",
#         "description": "The result of adding number1 and number2 together."
#     }
# } 

print(create_json_autoagent('create a function that would return the sum of two numbers'))

# print(single_turn_pseudofunction('add two numbers that would sum to 10', func))
##testing func end

