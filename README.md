# Pattern for Detecting Changes to Standards using Reasoning Models   

## Overview 

This pattern is designed to analyse and detect changes to standards using the capabilities of reasoning models in Azure OpenAI.
By leveraging Azure OpenAI's reasoning models, the script can:
  
- Parse PDF documents into markdown format
- Review 2 versions of the same document and detect the superseded & current versions
- Review both versions of the document, identify the sections containing standards and capture the changes between superseded and current versions
- Use different levels of reasoning (low, medium and high) to analyse the documents
- Review the current version and write a short summary
- Publish the findings in a report
  
## Getting Started

To prepare your environment for running this codebase, follow the steps outlined in the [Setup](./SETUP.md).

Once done, add the 2 PDF documents to be analysed to the source folder.

## Run the Analyser

To run the analyser, simply execute the `run.sh` or `run.ps1` script.

There are a number of command line arguments that you can pass to control the behaviour of the script.

If in doubt, simply run the script with the `--help` argument, and it will display a short help message that includes a brief explanation of each argument.

Here's a brief overview of the configuration options: 

| Command Argument         | Environment Variable       | Default            | Description                                                                                         | 
|--------------------------|----------------------------|--------------------|-----------------------------------------------------------------------------------------------------|
| `--openai-key`           | `AZURE_OPENAI_API_KEY`     | <not specified>    | The API Key to use for the Azure OpenAI API                                                         |
| `--openai-endpoint`      | `AZURE_OPENAI_ENDPOINT`    | <not specified>    | URL of the API Endpoint to use for the Azure OpenAI API                                             |
| `--openai-api-version`   | `AZURE_OPENAI_API_VERSION` | 2024-12-01-preview | Specifies the API Version to use                                                                    |
| `--reasoning-model`      | `REASONING_MODEL`          | o3-mini            | The name of the model deployment to use for reasoning                                               |
| `--reason-effort`        | `REASON_EFFORT`            | medium             | Effort to put into reasoning (low, medium, high)                                                    |
| `--source-dir`           | `SOURCE_DIR`               | source             | The path to the directory where the source PDF files are to be found                                | 
| `--interim-dir`          | `INTERIM_DIR`              | interim            | The path to the directory where the interim files will be written                                   |
| `--output-dir`           | `OUTPUT_DIR`               | output             | The path to the directory where the report files will be written                                    |