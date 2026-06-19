import json
from langchain_core.messages import HumanMessage
from src.retrieve import retrieve
from src.llm import llm


def generate_final_answer(query: str):
    """Generate final answer using multimodal retrieved content."""
    try:
        print(type(llm))
        chunks = retrieve(query)
        if not chunks:
            return "I couldn't find any relevant information."

        prompt_text = f"""
Based on the following retrieved documents, answer the user's question.

Question:
{query}

CONTENT TO ANALYSE:

"""
        message_content = [
            {
                "type": "text",
                "text": ""
            }
        ]
        for i, chunk in enumerate(chunks):
            prompt_text += f"\n----------- Document {i+1} -----------\n\n"
            if "original_content" in chunk.metadata:
                original_data = json.loads(chunk.metadata["original_content"])
                raw_text = original_data.get("raw_text", "")
                if raw_text:
                    prompt_text += f"TEXT:\n{raw_text}\n\n"
                tables_html = original_data.get("tables_html", [])
                if tables_html:
                    prompt_text += "TABLES:\n"
                    for j, table in enumerate(tables_html):
                        prompt_text += f"Table {j+1}:\n{table}\n\n"

            else:
                prompt_text += chunk.page_content + "\n\n"

        prompt_text += """
Please answer the question using ONLY the information provided above.
If the documents do not contain enough information, respond with:
"I don't have enough information to answer that question."
If images are relevant, use them while answering.

ANSWER:
"""
        message_content[0]["text"] = prompt_text
        for chunk in chunks:
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
        message = HumanMessage(content=message_content)
        print("LLM:", llm)
        print("LLM type:", type(llm))
        print("LLM invoke:", llm.invoke)
        response = llm.invoke([message])
        return response.content

    except Exception as e:
        print(f"Answer generation failed: {e}")
        return "Sorry, I encountered an error while generating the answer."