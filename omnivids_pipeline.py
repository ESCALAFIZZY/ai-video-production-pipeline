import os
import json
import re
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

from google import genai
from google.genai import types


# 1. Define the exact JSON structure we want Gemini to generate
class Scene(BaseModel):
    scene_id: int
    scene_name: str
    target_duration_sec: float
    script_line: str
    voiceover_pacing: str
    video_motion_prompt: str
    camera_motion: str
    motion_bucket_id: int


class Storyboard(BaseModel):
    scenes: list[Scene]


class OmnividsPipeline:
    WORDS_PER_MINUTE = 145

    def __init__(self, workspace_root: str = "OMNIVIDS_Production"):
        self.workspace_root = Path(workspace_root)
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.session_dir = self.workspace_root / self.date_str

        # Initialize the official Google GenAI SDK Client
        # This automatically securely loads your GEMINI_API_KEY environment variable
        self.ai_client = genai.Client()

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "_", slug)

    def _calculate_est_duration(self, text: str) -> float:
        words = len(text.split())
        return round((words / self.WORDS_PER_MINUTE) * 60, 2)

    def scaffold_project_workspace(self, topic_slug: str) -> dict:
        project_dir = self.session_dir / topic_slug
        subdirs = {
            "root": project_dir,
            "scripts": project_dir / "scripts",
            "voiceover": project_dir / "voiceover",
            "video_clips": project_dir / "video_clips",
            "renders": project_dir / "renders",
        }
        for path in subdirs.values():
            path.mkdir(parents=True, exist_ok=True)
        return subdirs

    def construct_scene_graph(self, topic: str) -> list:
        print(f"[*] Calling Gemini API to generate storyboard for: '{topic}'...")

        prompt = (
            f"You are a viral short-form video director. Generate a 4-scene storyboard for a vertical video (9:16) "
            f"about the topic: '{topic}'. Keep the total script length under 60 seconds. "
            f"Provide intense, cinematic T2V (Text-to-Video) motion prompts and precise camera motions "
            f"(e.g., 'fast_push_in', 'slow_orbit', 'drone_reveal'). Provide motion_bucket_id between 50 and 150."
        )

        # 2. Call the Gemini API with Structured Output constraints
        response = self.ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Storyboard,
                temperature=0.7,
            ),
        )

        # The API guarantees the response is formatted as valid JSON matching our Pydantic model
        data = json.loads(response.text)
        return data["scenes"]

    def generate_production_package(self, topic: str) -> Path:
        topic_slug = self._slugify(topic)
        workspace = self.scaffold_project_workspace(topic_slug)

        # Dynamically generate the content using Gemini
        scene_graph = self.construct_scene_graph(topic)

        full_script = " ".join(scene["script_line"] for scene in scene_graph)
        total_word_count = len(full_script.split())
        est_runtime_sec = sum(self._calculate_est_duration(s["script_line"]) for s in scene_graph)

        manifest = {
            "metadata": {
                "project_name": "OMNIVIDS Automation Pipeline",
                "topic": topic,
                "topic_slug": topic_slug,
                "created_at": datetime.now().isoformat(),
                "aspect_ratio": "9:16",
                "total_words": total_word_count,
                "estimated_runtime_seconds": est_runtime_sec
            },
            "audio_profile": {
                "engine": "ElevenLabs",
                "full_transcript": full_script
            },
            "timeline": scene_graph
        }

        manifest_path = workspace["scripts"] / "pipeline_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)

        brief_path = workspace["scripts"] / "production_brief.md"
        with open(brief_path, "w", encoding="utf-8") as f:
            f.write(f"# OMNIVIDS Production Brief: {topic}\n\n")
            f.write(f"- **Runtime:** ~{est_runtime_sec}s ({total_word_count} words)\n")
            f.write(f"- **Audio Transcript:**\n> {full_script}\n\n")
            f.write("## Shot List & Video Motion Prompts\n\n")
            for scene in scene_graph:
                f.write(f"### Scene {scene['scene_id']}: {scene['scene_name']}\n")
                f.write(f"- **Voiceover:** \"{scene['script_line']}\"\n")
                f.write(f"- **Pacing:** {scene['voiceover_pacing']}\n")
                f.write(f"- **Camera Motion:** `{scene['camera_motion']}`\n")
                f.write(f"- **T2V Video Prompt:**\n> {scene['video_motion_prompt']}\n\n")

        print(f"[*] Success! Production brief created at: {brief_path}")
        return manifest_path


if __name__ == "__main__":
    pipeline = OmnividsPipeline()
    print("=== OMNIVIDS Autonomous Production Pipeline (Gemini Powered) ===")

    while True:
        topic_input = input("\nEnter video concept (or 'exit' to quit): ").strip()
        if topic_input.lower() in ["exit", "quit", "q"]:
            break
        if not topic_input:
            continue

        try:
            pipeline.generate_production_package(topic_input)
        except Exception as e:
            print(f"Error communicating with API: {e}")
            print("Did you forget to restart your terminal after setting GEMINI_API_KEY?")