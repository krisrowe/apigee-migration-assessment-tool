# Contributing to Apigee Migration Assessment Tooling

First off, thank you for considering contributing to Apigee Migration Assessment Tooling ! We appreciate your time and effort. 

Here's how you can get involved:

## Reporting Bugs

* **Check existing issues:** Before submitting a new bug report, please search the [Issues](link to your project's issues page) to see if the issue has already been reported.
* **Provide detailed information:** When reporting a bug, please include:
    * **Clear and concise description:** Explain the problem you encountered.
    * **Steps to reproduce:** Provide detailed steps to reproduce the bug.
    * **Expected behavior:** Describe what you expected to happen.
    * **Actual behavior:** Describe what actually happened.
    * **Environment details:** Include information about your operating system, Python version, and any relevant dependencies.
    * **Screenshots or code snippets:** If applicable, include screenshots or code snippets to illustrate the issue.

## Suggesting Enhancements

We welcome suggestions for new features or improvements to existing functionality. When suggesting an enhancement:

* **Provide a clear description:** Explain the enhancement you're proposing.
* **Explain the benefits:** Describe how the enhancement would benefit users.
* **Consider alternatives:** If possible, suggest alternative approaches or solutions.

## Submitting Code Changes

We welcome code contributions! Here's how to submit a pull request:

1. **Fork the repository:** Click the "Fork" button in the top right corner of the repository page.
2. **Clone the forked repository:** `git clone https://github.com/your-username/your-forked-repo.git`
3. **Create a new branch:** `git checkout -b my-new-branch`
4. **Make your changes:** Implement your bug fix or enhancement.
5. **Commit your changes:** `git commit -am "Fix: Issue with [issue number]"`
6. **Push to your forked repository:** `git push origin my-new-branch`
7. **Create a pull request:** Go to the original repository and click the "New pull request" button. Select your forked repository and branch.
8. **Provide a detailed description:** Explain the changes you made and why.

## Debugging User Report Generation

To debug report generation issues, you can reproduce the exact state of a user's environment by running the tool locally with their `export_data.json` file. This method is 100% local and does not require any connection to a source or target Apigee organization.

1.  **Prepare the Directory:** Place the user's `export_data.json` file in the expected path. The tool will look for it here by default.
    ```bash
    mkdir -p ./output/export/
    cp /path/to/user/export_data.json ./output/export/
    ```

2.  **Run the Tool Locally:** Execute the main script with the following flags.
    ```bash
    python main.py --resources apis --skip-target-validation
    ```

### Key Command-Line Arguments

*   `--resources <value>`: **This flag is syntactically required** by the script's argument parser. However, because the presence of a valid `export_data.json` causes the entire export phase to be skipped, the value you provide (e.g., `apis`, `all`) is ignored.
*   `--skip-target-validation`: **This flag is a crucial safeguard.** It explicitly prevents the tool from attempting to run the validation phase against a target Apigee environment. This guarantees the tool remains in a local-only mode, which is essential when you do not have access to a user's target environment.

### How It Works

The tool is designed to prioritize existing data to allow for reruns and debugging:

1.  **File Detection:** On startup, the tool checks for the existence of `output/export/export_data.json`.
2.  **Integrity Check:** If the file exists, it then checks if the file contains the key-value pair `"export": true`. This flag serves as a sentinel value, confirming that the data is from a previous, **complete and successful** export.
3.  **Execution Flow:**
    *   If the file and the flag are present, the entire **source export phase is skipped**.
    *   If `--skip-target-validation` is used, the **target validation phase is also skipped**.
    *   The tool then proceeds directly to the final step: generating the `qualification_report.xlsx` using only the data contained within the local JSON file.

## Code Style

* **Follow PEP 8:** Adhere to the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/) for Python code.
* **Use meaningful names:** Choose descriptive names for variables, functions, and classes.
* **Write clear comments:** Explain the purpose and functionality of your code.
* **Keep functions short:** Break down complex tasks into smaller, more manageable functions.

## Testing

* **Write unit tests:** Ensure your code changes are well-tested by writing unit tests.
* **Run existing tests:** Before submitting a pull request, make sure all existing tests pass.

## Code of Conduct

We expect all contributors to adhere to our [Code of Conduct](link to your project's code of conduct). Please treat everyone with respect and courtesy.

## Questions

If you have any questions or need help getting started, feel free to [open an issue](link to your project's issues page) or contact us.

Thank you for your contributions!