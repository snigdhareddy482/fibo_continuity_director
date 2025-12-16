# FIBO Continuity Director
**JSON-Native Multi-Shot Storyboarding with Refine & Reel Export**

## Overview

**FIBO Continuity Director** is an AI-powered cinematic planning and generation tool built for the **FAL.AI / Bria FIBO Challenge**. It bridges the gap between text briefs and consistent visual storylines by orchestrating a structured "Director's Plan" (JSON) into high-fidelity image sequences.

The system uses a **Planner Agent** to break down a brief (e.g., "A cyberpunk detective in rain") into a coherent list of shots, ensuring visual continuity through shared camera, lighting, and palette parameters ("ContinuityMap"). It leverages the **FAL FIBO API** for both initial text-to-image generation and subsequent image-to-image refinement (ComfyUI-style "Refine"), allowing users to maintain character and environmental consistency across shots.

Finally, the tool validates visual coherence using color histogram metrics and automatically compiles the sequence into a **Storyboard Grid** (PNG) and an **MP4 Video Reel**, ready for creative review.

## Key Features & Competition Alignment

### 1. Best Overall (JSON-Native & Pro Features)
*   **Deep JSON Integration**: The core engine runs on a strict `ContinuityMap` schema (Pydantic), ensuring every pixel generated is the result of structured data, not random prompting.
*   **Professional Quality**: Built-in support for **HDR** workflows and **16-bit** color depth configuration in `config.py` and `schemas.py`, pushing the boundaries of enterprise visual AI.

### 2. Best Controllability
*   **Parametric Directing**: Users don't just "prompt"; they adjust **Lens (mm)**, **Color Temperature (K)**, and **Lighting Setups** via UI sliders.
*   **Disentangled Controls**: Camera angles, lighting, and composition rules are managed independently, allowing for precise tweaks without destroying the image's essence.
*   **Multimodal Refinement**: "Refine" mode uses Image-to-Image (ControlNet-style) logic to iterate on shots while preserving composition.

### 3. Agentic Workflow
*   **Planner Agent**: Transforms vague text briefs into rigorous `ProjectPlan` JSON objects, automating the most tedious part of pre-production.
*   **Self-Healing**: The continuity validator automatically flags outliers in the sequence, enabling a loop where the agent can potentialy re-shoot bad takes (simulated).

### 4. Professional UX
*   **Director's Dashboard**: A Streamlit interface designed for creatives, featuring exportable **Storyboard Grids** and **MP4 Reels** for immediate dailies review.
*   **Asset Management**: Clean separation of `storyboard` vs `product` modes for distinct commercial use cases.

## Other Capabilities
-   **Multi-Shot Generation**: Batch generation using `text2img` based on the structured plan.
-   **Exports**: 
    -   **JSON Plan**: Portable project definition.
    -   **Storyboard Grid**: High-res PNG contact sheet.
    -   **MP4 Reel**: Smooth image sequence video for dailies/review.

## Architecture

The project follows a modular architecture designed for extensibility:

-   **`app/ui/main.py`**: The Streamlit frontend. Handles user input, state management, and interaction.
-   **`app/core/planner.py`**: Simulates an LLM agent. Converts text briefs into the JSON `ProjectPlan` schema using heuristic templates.
-   **`app/core/engine.py`**: The core orchestrator. Builds API payloads from the ContinuityMap and ShotSpecs, and manages the generation loop.
-   **`app/core/client.py`**: Wrapper for the Bria FIBO API. Handles text-to-image generation with polling support.
-   **`app/core/validator.py`**: Image analysis module. Computes HSV color distance metrics and provides auto-fix logic.
-   **`app/models/schemas.py`**: Pydantic models enforcing the rigorous JSON structure (`ProjectPlan`, `ContinuityMap`).
-   **`app/utils/helpers.py`**: Media processing helpers using Pillow (Grids) and MoviePy (Video).

```ascii
User Input
    │
    ▼
[ UI App ] ───▶ [ Planner Agent ] ───▶ { ProjectPlan JSON }
    │                                          │
    ▼                                          ▼
[ Continuity Engine ] ◀─────────────── [ Schemas ]
    │
    ├──▶ [ FIBO Client ] ───▶ ( FAL.AI / Bria API )
    │            │                    │
    │            ◀────────────────────┘
    │
    ├──▶ [ Validator ] (Metrics & consistency checks)
    │
    ▼
[ Utils ] ───▶ [ Storage: outputs/ ]
                    ├── images/
                    ├── storyboard.png
                    └── reel.mp4
```

## Setup & Installation

1.  **Clone and Enter Directory**:
    ```bash
    git clone https://github.com/your/repo.git
    cd fibo_continuity_director
    ```

2.  **Create Virtual Environment** (Recommended):
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Set your API credentials. You can set them in your terminal or create a `.env` file (if you add `python-dotenv` support).
    ```bash
    # Windows Powershell
    $env:FIBO_API_URL="https://engine.prod.bria-api.com/v2/image/generate"
    $env:FIBO_API_KEY="your_api_key_here"
    ```

5.  **Run the App**:
    ```bash
    streamlit run app/ui/main.py
    ```

## Usage

1.  **Briefing**: In the sidebar, enter a description (e.g., "A futuristic Formula 1 car pit stop"). Select **Mode** ("product" or "storyboard") and number of shots.
2.  **Generate Plan**: Click **"Generate Plan & Sequence"**. The Planner will create a shot list and the Engine will generate the initial images.
3.  **Review & Tweak**:
    -   Look at the "Continuity Controls" expander. Adjust **Lens**, **Lighting Temp**, or **Palette** and click **"Apply Continuity & Re-Generate"** to re-shoot the whole sequence with new global settings.
4.  **Refine**:
    -   If a specific shot is off, click **"Refine this shot"**.
    -   Optionally, upload a specific base image (e.g., a sketch or a previous good shot) to usage as the reference input for the refinement.
5.  **Export**:
    -   Scroll to the "Exports" section.
    -   Download the **Storyboard Grid** or generate and download the **MP4/Video Reel**.

## Hackathon Notes

This project was built to explore the capabilities of the **FAL.AI / Bria FIBO** model family:

-   **Structure-First Control**: Instead of just prompting, we map the **Bria parameter documentation** (Camera, Lighting, etc.) to a strict Pydantic schema, ensuring the model receives highly structured inputs.
-   **Refinement Loop**: Inspired by **ComfyUI's generate/refine workflows**, the "Refine" feature uses the API's image-to-image capabilities (passing the `images` array in the payload) to lock in composition while iterating on style.
-   **Model Card Alignment**: The prompts are constructed to align with the training data concepts described in the HuggingFace model cards for Bria (e.g., specific lighting terminologies).

## Limitations & Future Work

-   **Planner Intelligence**: Currently uses a deterministic "Mock LLM" for reliability during the demo. A real implementation would call GPT-4/Gemini to generate the JSON plan dynamically.
-   **Continuity Metrics**: Current validation uses simple color histograms. Future work could use CLIP embeddings or FaceID to ensure strict subject consistency.
-   **Production Integration**: Enhanced support for 16-bit pipelines and EXR export for professional VFX workflows.
