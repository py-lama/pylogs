# LogLama Ansible Tests

This directory contains Ansible playbooks and scripts for testing LogLama in different environments. These tests help identify issues with environment interactions such as shell commands, API calls, and SQL database operations.

## Requirements

- Ansible 2.9 or higher
- Python 3.6 or higher
- LogLama installed or available in the project path

## Test Structure

The test suite includes the following components:

1. **Environment Variable Tests**: Verify that LogLama can properly access and use environment variables
2. **Shell Command Tests**: Test logging of shell command execution
3. **SQL Database Tests**: Verify database logging and context handling with SQLite
4. **API Interaction Tests**: Test logging of API requests and responses
5. **Diagnostic Tools**: Run LogLama diagnostic tools to identify any issues

## Running the Tests

### Local Testing

To run the tests on your local machine:

```bash
cd /path/to/loglama/tests/ansible
ansible-playbook -i inventory.ini loglama_test_playbook.yml --limit local
```

### Remote Testing

To test LogLama on remote hosts:

1. Add the remote hosts to the `inventory.ini` file
2. Run the playbook with the remote group:

```bash
ansible-playbook -i inventory.ini loglama_test_playbook.yml --limit remote
```

### Testing Specific Components

To test only specific components, use Ansible tags (to be added in future versions).

## Interpreting Results

The playbook will output detailed results for each test. Look for:

- `SUCCESS` messages indicating passed tests
- `FAILED` messages indicating test failures
- Detailed error messages for troubleshooting

A diagnostic report will be generated at `/tmp/loglama_ansible_test/diagnostic_report.json` with comprehensive information about any issues found.

## Adding Custom Tests

To add custom tests:

1. Create a new Python script in the test directory
2. Add a new task block in the `loglama_test_playbook.yml` file
3. Ensure your test script outputs clear success/failure messages

## Troubleshooting

If the tests fail:

1. Check that LogLama is properly installed
2. Verify that the Python path is correctly set
3. Check file permissions for log and database files
4. Review the diagnostic report for detailed information
