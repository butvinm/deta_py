[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![Linters](https://github.com/butvinm/deta_py/workflows/linting/badge.svg)](https://github.com/butvinm/deta_py/actions)
[![Tests](https://github.com/butvinm/deta_py/workflows/tests/badge.svg)](https://github.com/butvinm/deta_py/actions)

# DetaPy

> It is still in development

Yet another [Deta Space](https://deta.space/) SDK for Python.

But this one is:
- Fully typed
- Well tested
- Follow pythonic style and conventions
- Pass strongest linter
- Probably actively maintained

## Installation

You can install the Deta Base Python SDK using pip:

> But not now, because it's not published yet.

```bash
pip install deta-py
```

## Getting Started

### Importing the SDK

To use the Deta Base SDK in your Python application, you need to import it as follows:

```python
from deta_py.deta_base.base import DetaBase

# or async version
from deta_py.deta_base.async_base import AsyncDetaBase
```

### Initialize Deta Base Client

To get started, you need to initialize a Deta Base client by providing your Data Key and the name of the base you want to work with. You can obtain the Data Key from your Deta [project or collection settings](https://deta.space/docs/en/build/fundamentals/data-storage#data-keys).

```python
data_key = 'your_data_key_here'
base_name = 'your_base_name_here'

db = DetaBase(data_key, base_name)
```

## Usage

The DetaBase provides several methods for interacting with your Deta Base. Below are some common operations:

### Putting Items

You can use the `put` method to add or update items in your Deta Base. It supports batch operations for efficient processing.

```python
items = [
    {'value': 1},
    {'value': 2}
]

# Put the items into the base
processed_items = db.put(*items)
# processed_items == [{'key': '012345678910', 'value': 1}, {'key': '123456789101', 'value': 2}]
```

### Getting an Item

Retrieve an item from the base using its key:

```python
item = db.get('key1')
if item is not None:
    print('Retrieved item:', item)
else:
    print('Item not found')
```

### Deleting an Item

Delete an item from the base using its key:

```python
db.delete('key1')
```

### Inserting an Item

Insert an item into the base. If an item with the same key already exists, it will not be inserted.

```python
item = {'key3': 'value3', 'value': 1}

# Insert the item into the base
inserted_item = db.insert(item)
if inserted_item is not None:
    print('Inserted item:', inserted_item)
else:
    print('Item with the same key already exists')
```

### Updating an Item

Update an item in the base using various operations like setting fields, incrementing values, appending to lists, and deleting fields:

```python
key = 'key1'

# Create an update request
operations = ItemUpdate()
operations.set(name='John')
operations.increment(age=1)
operations.append(friends=['Jane'])
operations.delete('hobbies')

# Update the item with the specified key
success = db.update(key, operations)

if success:
    print('Item updated successfully')
else:
    print('Item not found')
```

### Querying Items

You can query items in the base based on specific criteria:

```python
# Define a query (example: retrieve items where 'age' is greater than 18)
query = [
    {'age?gt': 18, 'age?lt': 20}, # age > 18 and age < 20
    {'age?gt': 30, 'age?lt': 35}, # or age > 30 and age < 35
]

# Query the base
result = db.query(query)

# Retrieve items and handle pagination if necessary
items = result.items
while result.last:
    result = db.query(query, last=result.last)
    items += result.items
```

## Contributing

We welcome contributions to this SDK. Feel free to open issues or submit pull requests on [GitHub](https://github.com/butvinm/deta_py).

Also see [CONTRIBUTING.md](https://github.com/butvinm/deta_py/blob/master/CONTRIBUTING.md) for more information on how to contribute.

## License

This SDK is licensed under the MIT License. See the [LICENSE](https://github.com/butvinm/deta_py/blob/master/LICENSE) file for details.
