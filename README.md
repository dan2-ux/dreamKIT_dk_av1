#dk_av1

Welcome to the official repository for dk_av1, a powerful AI-driven tool designed to seamlessly integrate natural language understanding with automation on the dreamKIT platform. This repository provides everything you need to get dk_av1 up and running on your local machine.
🧠 What is dk_av1?

dk_av1 is an AI-powered application built using the LangGraph framework. It is designed to interpret and process user input using state-of-the-art language models and carry out intelligent automation tasks on dreamKIT, a customizable execution environment.

By leveraging AI, dk_av1 can:

    Parse and understand user commands or instructions.

    Translate natural language into actionable operations.

    Interface with dreamKIT to perform specific, predefined tasks automatically.

This project aims to demonstrate how conversational AI can be embedded into real-world automation pipelines, making it easier for users to interact with complex systems using plain language.
⚙️ Prerequisites

Before running dk_av1, ensure the following tools are installed on your local machine:

    Ollama – A tool for running large language models locally.

    Docker – To containerize and execute the application in a consistent environment.

    A compatible AI model – Choose and pull your preferred AI model via Ollama.

📦 Installation and Setup

Follow these steps to set up and run dk_av1:
1. Install Ollama

If you haven’t already, install Ollama by following the instructions on the Ollama website. Once installed, use the CLI to pull the AI model of your choice. For example:

ollama pull llama3

Replace llama3 with your preferred AI model.
2. Configure the AI Model

Open the define.json file located in the root directory of this repository. Update the configuration to match the AI model you have pulled with Ollama. This step is essential to ensure dk_av1 uses the correct backend model.

3. Build the Docker Image

To containerize dk_av1, use the following command to build the Docker image:

<pre>docker build -t dk_av1 .</pre>

This command will create a local Docker image named dk_av1 based on the configuration and code provided in this repository.
4. Run the Docker Container

Once the image is built, you can run dk_av1 using the command below:

    docker run -it --rm --name dk_av1 --net=host --device=/dev/snd dk_av1

Explanation of flags:

    -it: Runs the container in interactive mode.

    --rm: Automatically removes the container after it exits.

    --name dk_av1: Assigns a name to the container instance.

    --net=host: Uses the host's networking stack (required for some audio/network capabilities).

    --device=/dev/snd: Grants the container access to the sound device (if needed for audio output).
