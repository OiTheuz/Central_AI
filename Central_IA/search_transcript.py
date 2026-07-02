import json
import os

transcript_path = r"C:\Users\MouTh\.gemini\antigravity-ide\brain\0252188c-e3d7-487b-8d69-b0d51f40fd93\.system_generated\logs\transcript.jsonl"
with open("transcript_results.txt", "w", encoding="utf-8") as out:
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if "systemctl restart" in line:
                    data = json.loads(line)
                    if data.get("source") == "MODEL":
                        content = data.get("content", "")
                        if "systemctl restart" in content:
                            out.write(content + "\n---\n")
