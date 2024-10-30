# Library Management and Debugging Guide

This guide provides steps for debugging issues related to `pipenv` and `pip` installations, checking libraries, and removing unnecessary libraries in your environment.

## Table of Contents
1. [Checking Installed Libraries in `pipenv`](#checking-installed-libraries-in-pipenv)
2. [Creating a `requirements.txt` File](#creating-a-requirementstxt-file)
3. [Deleting All Libraries Installed in `pip`](#deleting-all-libraries-installed-in-pip)

### Checking Installed Libraries in `pipenv`
If you want to view and verify the libraries installed in your `pipenv` environment, you can use the command:

```bash
pipenv check
```

This command checks for security vulnerabilities and verifies dependencies in your `pipenv` environment. To get a more detailed list of the installed packages, you can create a `requirements.txt` file and view its contents.

### Creating a requirements.txt File
1. Create a temporary requirements.txt file in your environment using:\
```bash
pipenv check
```
2. To display the contents of this file, use the cat command:
```bash
cat <path-to->requirements.txt
```

### Deleting All Libraries Installed in pip
If you accidentally installed libraries in your global pip environment and want to clean them up, follow these steps:
1. Export the list of installed libraries to a temporary file:
```bash
pip freeze > pip.txt
```
2. (Optional) Exclude specific libraries: Open pip.txt and remove the names of libraries you don't want to delete.
3. Uninstall libraries using the list:
```bash
pip uninstall -r pip.txt -y
```
4. Delete the pip.txt file to clean up:
```bash
rm pip.txt
```
