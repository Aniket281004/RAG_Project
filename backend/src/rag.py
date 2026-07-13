import json
from langchain_core.messages import HumanMessage
from src.retrieve import retrieve
from src.llm import llm
from src.utils import export_chunks_to_json

def generate_final_answer(query: str):
    """Generate a question paper using study material and previous year questions."""

    try:
        results = retrieve(query)
        study_chunks, pyq_chunks = results["study_material"], results["pyqs"]

        export_chunks_to_json(study_chunks, "study_results.json")
        export_chunks_to_json(pyq_chunks, "pyq_results.json")

        if not study_chunks and not pyq_chunks:
            return "I couldn't find any relevant information."

        message_content = [
            {
                "type": "text",
                "text": ""
            }
        ]

        prompt_text = f"""
You are an expert university paper setter.

Your task is to GENERATE a NEW question paper.

DO NOT answer any questions.

The generated paper should resemble the style, wording, difficulty and format of the provided Previous Year Questions.

Use the Study Material to determine the concepts that should be tested.

=========================
USER REQUEST
=========================

{query}

====================================================
STUDY MATERIAL (Concepts to test)
====================================================

"""


        for i, chunk in enumerate(study_chunks):

            prompt_text += f"\n========== Study Material {i+1} ==========\n\n"

            if "original_content" in chunk.metadata:

                original_data = json.loads(chunk.metadata["original_content"])

                raw_text = original_data.get("raw_text", "")

                if raw_text:
                    prompt_text += raw_text + "\n\n"

                tables = original_data.get("tables_html", [])

                if tables:
                    prompt_text += "Tables:\n"

                    for table in tables:
                        prompt_text += table + "\n\n"

            else:
                prompt_text += chunk.page_content + "\n\n"

        prompt_text += """

PREVIOUS YEAR QUESTIONS

These are ONLY references for:

- formatting
- marks distribution
- wording
- difficulty
- paper structure

Do NOT copy these questions.

"""

        for i, chunk in enumerate(pyq_chunks):

            prompt_text += f"\n========== PYQ {i+1} ==========\n\n"

            if "original_content" in chunk.metadata:

                original_data = json.loads(chunk.metadata["original_content"])

                raw_text = original_data.get("raw_text", "")

                if raw_text:
                    prompt_text += raw_text + "\n\n"

                tables = original_data.get("tables_html", [])

                if tables:
                    prompt_text += "Tables:\n"

                    for table in tables:
                        prompt_text += table + "\n\n"

            else:
                prompt_text += chunk.page_content + "\n\n"


        prompt_text += """
====================================================
INSTRUCTIONS
====================================================

Generate ONE complete university question paper.

Rules:

1. DO NOT answer any question.

2. Follow the SAME formatting and structure as the provided PYQs.

3. Follow the same marks distribution whenever possible.

4. Follow the same section names (Section A, B, C...) if present.

5. Use the Study Material to determine what topics should appear.

6. Do NOT repeat any previous year question verbatim.

7. You may:
   - slightly modify existing questions
   - combine multiple PYQs
   - increase/decrease difficulty
   - create entirely new questions

8. Ensure there is sufficient variation from the PYQs.

9. Maintain the same academic level.

10. Include diagrams/tables only if appropriate.

11. Return ONLY the generated question paper.

12. Do not include explanations, notes or answers.

13. The output should look like an actual university examination paper.

QUESTION PAPER:
"""
        # Images

        for chunk in study_chunks + pyq_chunks:

            if "original_content" not in chunk.metadata:
                continue

            original_data = json.loads(chunk.metadata["original_content"])

            images = original_data.get("images_base64", [])

            for image in images:

                message_content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}"
                        },
                    }
                )

        message_content[0]["text"] = prompt_text

        message = HumanMessage(content=message_content)

        response = llm.invoke([message])

        return response.content

    except Exception as e:
        print(f"Answer generation failed: {e}")
        return "Sorry, I encountered an error while generating the question paper."