#!/usr/bin/env python

from pathlib import Path
from time import sleep
import sys
import csv
import os
import json
import re as regex
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from openai import AzureOpenAI
from markitdown import MarkItDown
from tqdm import tqdm

import dotenv
dotenv.load_dotenv(".env")

reasoning_prompt = (Path(__file__).parent / "prompts/reasoning.txt").read_text()

def run_prompt(client: AzureOpenAI, model: str, dev_prompt:str, user_prompt:str, reason_effort:str) -> str:
    retries = 10
    
    while retries > 0:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    { "role": "developer", "content": dev_prompt}, 
                    {"role": "user", "content": user_prompt}
                ],
                reasoning_effort=reason_effort  
            )
            
            response = completion.choices[0].message.content
            
            if response is not None and len(response) > 0:
                return response
            retries -= 1

        except Exception as e:
            msg = f"{e}"
            if "429" in msg:
                sleep(10)
                retries -= 1
            else: 
                retries -= 2
                sleep(1)
            if retries <= 0:
                raise e
    raise Exception("Failed to get response - too many failed attempts to run prompt")

def parse_file(file: Path) -> str:
    try:
        md = MarkItDown()
        result = md.convert(f"{file}")
        return result.text_content
    
    except Exception as e:
        print(f"[{file.stem}] Failed to parse PDF: {e}")
        return None

def process_file(file: Path, interim_path: Path) -> str:
    metadata = None
    try:
        interim_file = interim_path / (file.stem + ".md")
        print(f"[{file.stem}] Parsing source")
        source_md = parse_file(file)
        
        if source_md is None: 
            raise Exception("Failed to parse source file")
        
        with open(interim_file, "w", encoding="UTF-8") as f:
            f.write(source_md)

        return source_md
    except Exception as e:
        print(f"[{file.stem}] Error: {e}")

def main(args: dict[str, str]) -> None: 

    if args.get("--help", False):
        print("Usage: ./workflow.py <args>")
        print("Arguments:")
        print("--openai-key=<key> : OpenAI API Key")
        print("--openai-endpoint=<endpoint> : OpenAI Endpoint")
        print("--openai-api-version=<version> : OpenAI API Version")
        print("--reasoning-model=<model> : AI Model deployment to use for reasoning")
        print("--reason-effort=<low|medium|high> : Effort to put into reasoning")
        print("--source-dir=<dir> : Source Directory (where the source PDFs are stored)")
        print("--interim-dir=<dir> : Interim Directory (where the interim files are stored)")
        print("--output-dir=<dir> : Output Directory (where the final report is stored)")
        return
    
    openai_key = args.get("--openai-key", os.getenv("AZURE_OPENAI_API_KEY"))
    if openai_key is None:
        print("Please provide an OpenAI key using the --openai-key flag or in a .env file with the key OPENAI_KEY")
        return
    
    openai_endpoint = args.get("--openai-endpoint", os.getenv("AZURE_OPENAI_ENDPOINT"))
    if openai_endpoint is None:
        print("Please provide an OpenAI endpoint using the --openai-endpoint flag or in a .env file with the key OPENAI_ENDPOINT")
        return
    
    openai_api_version = args.get("--openai-api-version", os.getenv("AZURE_OPENAI_API_VERSION"))
    if openai_api_version is None:
        openai_api_version = "2024-12-01-preview"

    reasoning_model = args.get("--reasoning-model", os.getenv("REASONING_MODEL"))
    if reasoning_model is None:
        reasoning_model = "o3-mini"

    client = AzureOpenAI(
        api_key=openai_key,
        azure_endpoint=openai_endpoint,
        api_version=openai_api_version,
    )

    source_dir = args.get("--source-dir", os.getenv("SOURCE_DIR"))
    if source_dir is None:
        source_dir = "source"
    
    interim_dir = args.get("--interim-dir", os.getenv("INTERIM_DIR"))
    if interim_dir is None:
        interim_dir = "interim"
    
    output_dir = args.get("--output-dir", os.getenv("OUTPUT_DIR"))
    if output_dir is None:
        output_dir = "output"

    reason_effort = args.get("--reason-effort", os.getenv("REASON_EFFORT"))
    if reason_effort is None:
        reason_effort = "medium"

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"Source directory {source_dir} does not exist")
        return
    
    interim_path = Path(interim_dir)
    if not interim_path.exists():
        interim_path.mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    supported_file_types = ['.pdf']

    user_prompt = ""
    files = [file for file in source_path.iterdir() if file.suffix in supported_file_types]

    if len(files) != 2:
        raise Exception("There must be exactly 2 files in the source directory.")

    for file in files:
        try:
            user_prompt += "\n\n\nA VERSION OF THE FILE -- \n\n\n" + process_file(file, interim_path)

        except Exception as e:
            print(f"Failed to submit file {file.stem} for processing: {e}")

    # print(user_prompt)

    output = run_prompt(client, reasoning_model, reasoning_prompt, user_prompt, reason_effort)
    # print(output)

    output_file = output_path / ("output.md")
    with open(output_file, "w", encoding="UTF-8") as f:
        f.write(output)

    print(f"Reasoning completed!")

def _parse_args() -> dict[str, str]:
    args = sys.argv[1:]
    if len(args) == 0:
        return {}
    res = {}
    for arg in args:
        if arg.startswith("--"):
            arr = arg.split("=")
            key = arr[0]
            value = arr[1] if len(arr) > 1 else True
            res[key] = value
    return res

if __name__ == "__main__":
    args = _parse_args()
    main(args)
