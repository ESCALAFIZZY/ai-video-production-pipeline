# ai-video-production-pipeline
An autonomous Python pipeline utilizing the Gemini API and Pydantic to generate structured storyboards, video motion prompts, and automated directory systems for short-form AI content production.

OMNIVIDS Automated Production Pipeline
Overview
The OMNIVIDS pipeline is an autonomous backend orchestration system built in Python. It is designed to eliminate manual friction in short-form video production by utilizing Large Language Models (LLMs) to generate structured storyboards, precise Text-to-Video (T2V) motion prompts, and organized file directories.

Architecture & Tech Stack
Language: Python 3.x

AI Integration: Google GenAI SDK (Gemini 2.5 Flash)

Data Validation: Pydantic

Data Structures: JSON, Markdown

Key Features
Strict Schema Generation: Utilizes Pydantic to enforce structured JSON outputs from the Gemini API, ensuring the AI returns machine-readable arrays rather than conversational text.

Automated File Scaffolding: Dynamically provisions localized, date-stamped directory trees (scripts/, voiceover/, video_clips/, renders/) to isolate project assets.

Algorithmic Pacing Calculation: Computes estimated speech runtimes based on a calibrated 145-WPM target, ensuring final content strictly adheres to the 60-second limit for vertical video platforms.

Dual-Format Output: Generates both a pipeline_manifest.json for future direct API integrations (e.g., ElevenLabs) and a production_brief.md for human editorial review.

Usage
Clone the repository and install the dependencies:

Bash
pip install google-genai pydantic
Set your Google Gemini API key as an environment variable:

Bash
setx GEMINI_API_KEY "your_api_key_here"
Execute the pipeline:

Bash
python omnivids_pipeline.py
Enter a topic prompt via the CLI. The system will automatically construct the project directory and populate the production deliverables
