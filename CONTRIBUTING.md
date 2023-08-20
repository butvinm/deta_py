# Contributing to the DetaPy

Thank you for considering contributing to the DetaPy!

## Table of Contents

- [Contributing to the DetaPy](#contributing-to-the-detapy)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Setting Up Testing](#setting-up-testing)
  - [Coding Guidelines](#coding-guidelines)
    - [Code Style](#code-style)
    - [Type Annotations](#type-annotations)
    - [Testing](#testing)
  - [Reporting Issues](#reporting-issues)
  - [Submitting Pull Requests](#submitting-pull-requests)
  - [License](#license)

## Getting Started

### Prerequisites

Before you begin contributing to the DetaPy, make sure you have the following prerequisites installed:

- [Python](https://www.python.org/downloads/) (3.9 or higher)
- [Poetry](https://python-poetry.org/docs/#installation) for project management

### Installation

1. Fork the [DetaPy repository](https://github.com/butvinm/deta_py) on GitHub.
2. Clone your forked repository to your local machine:

   ```bash
   git clone https://github.com/butvinm/deta_py
   ```

3. Navigate to the project directory:

   ```bash
   cd deta_py
   ```

4. Install the project dependencies using Poetry:

   ```bash
   poetry install
   ```

Now you're ready to start contributing to the project!

## Setting Up Testing

To run tests for the DetaPy, you'll need to set up testing configuration:

1. Copy the `.env.example` file to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and provide values for the `TEST_DATA_KEY` and `TEST_BASE_NAME` variables.

## Coding Guidelines

### Code Style

The DetaPy follows the [Wemake Python Styleguide](https://wemake-python-stylegui.de/en/latest/). Before submitting your code changes, run the following command to check for code style violations:

```bash
poetry run flake8 deta_py
```

Make sure your code conforms to the style guide to maintain consistency in the project.

### Type Annotations

The SDK uses type annotations extensively, and we recommend following the type hints provided in the code. You can use [mypy](http://mypy-lang.org/) to check for type errors:

```bash
poetry run mypy deta_py
```

Please ensure that your code has accurate type annotations to improve code clarity and maintainability.

### Testing

Before submitting a pull request, ensure that your code changes include relevant unit tests. You can run the tests using [pytest](https://docs.pytest.org/en/latest/):

```bash
poetry run pytest tests
```

Make sure all tests pass successfully, and consider adding new tests to cover any added functionality or changes.

## Reporting Issues

If you encounter any issues or have suggestions for improvements, please create a GitHub issue in the [DetaPy repository](https://github.com/butvinm/deta_py/issues). Provide detailed information about the problem or suggestion, including steps to reproduce the issue if applicable.

## Submitting Pull Requests

If you'd like to contribute code changes or new features to the DetaPy, please follow these steps:

1. Fork the [DetaPy repository](https://github.com/butvinm/deta_py) on GitHub.

2. Create a new branch for your changes:

   ```bash
   git checkout -b feat/your-feature-name
   ```

3. Make your code changes and commit them to your branch.

4. Push your branch to your forked repository:

   ```bash
   git push origin feat/your-feature-name
   ```

5. Create a pull request (PR) in the [DetaPy repository](https://github.com/butvinm/deta_py) to propose your changes.

6. In your PR, provide a clear description of the changes you've made and why they are necessary.

7. Ensure that your code passes all tests, follows the coding guidelines, and includes any necessary documentation updates.

8. Once your PR is reviewed and approved, it will be merged into the main repository.

Thank you for your contributions to the DetaPy!

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](https://github.com/butvinm/deta_py/blob/master/LICENSE).
