import json
import random

# File paths
input_file = r".\super_qa_literature_v1.1\super_qa_literature_v1.1\label_part_0.jsonl"
output_file = "output1.jsonl"

processed_data = []

with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        json_data = json.loads(line.strip())
        original_data = json_data.copy()
        conversations = original_data.pop("conversations", [])

        num_images = len(original_data["image"])
        num_images = '<image>\\n' * num_images

        # Find last GPT response and human question
        gpt_response = None
        for conv in reversed(conversations):
            if conv["from"] == "gpt":
                gpt_response = conv["value"]
            if conv["from"] == "human":
                human_question = conv["value"]
                break

        gpt_json = json.loads(gpt_response)

        # Create sections (original format)
        sections = []
        all_questions = {}
        for idx, section in enumerate(gpt_json):
            section_copy = section.copy()
            section_copy["section_id"] = idx + 1
            if "questions" in section:
                all_questions[idx+1] = section["questions"]
            section_copy.pop("questions", None)
            sections.append(section_copy)

        # Initial conversation (unchanged)
        new_conversations = [
            {
                "from": "human",
                "value": f"{num_images}Phân tích bố cục văn bản"
            },
            {
                "from": "gpt",
                "value": {
                    "description": "Bố cục đề thi gồm các phần sau:",
                    "sections": sections
                }
            }
        ]

        # Process each section
        for j, part in enumerate(gpt_json):
            section_id = j + 1
            
            # Check if section has required keys for question extraction
            required_keys = ['command', 'number_question', 'type_answer', 'context', 'questions_id']
            has_required_keys = all(key in part for key in required_keys)
            
            if not has_required_keys:
                # Skip question extraction for this section
                continue
                
            if "questions" not in part or "questions_id" not in part:
                continue
                
            i = random.randint(1, 2)
            questions_list = part["questions_id"][0]
            questions_content_list = part["questions"]
            
            if len(questions_list) > i + 1:
                # Split questions into two parts
                questions_part_1 = questions_list[:i + 1]
                questions_part_2 = questions_list[i + 1:]
                
                questions_content_part_1 = questions_content_list[:i + 1]
                questions_content_part_2 = questions_content_list[i + 1:]

                # First part - list specific questions
                new_conversations.append({
                    "from": "human",
                    "value": f"Trích xuất nội dung các câu hỏi {', '.join(questions_part_1)} trong section {section_id} dưới dạng json"
                })
                new_conversations.append({
                    "from": "gpt",
                    "value": questions_content_part_1
                })

                # Second part - list specific questions
                new_conversations.append({
                    "from": "human",
                    "value": f"Trích xuất nội dung các câu hỏi {', '.join(questions_part_2)} trong section {section_id} dưới dạng json"
                })
                new_conversations.append({
                    "from": "gpt",
                    "value": questions_content_part_2
                })
            else:
                # Handle cases with few questions
                question_ids = part["questions_id"][0]
                
                if len(question_ids) == 1:
                    new_conversations.append({
                        "from": "human",
                        "value": f"Trích xuất nội dung câu hỏi {question_ids[0]} trong section {section_id} dưới dạng JSON"
                    })
                else:
                    new_conversations.append({
                        "from": "human",
                        "value": f"Trích xuất nội dung các câu hỏi {', '.join(question_ids)} trong section {section_id} dưới dạng JSON"
                    })
                
                new_conversations.append({
                    "from": "gpt",
                    "value": questions_content_list
                })

        # Final response with all questions
        final_response = {
            "description": "Bố cục đề thi đầy đủ bao gồm các phần và câu hỏi:",
            "sections": []
        }
        
        for section in sections:
            section_copy = section.copy()
            section_id = section_copy["section_id"]
            if section_id in all_questions:
                section_copy["questions"] = all_questions[section_id]
            final_response["sections"].append(section_copy)

        # Final prompt and response
        new_conversations.append({
            "from": "human",
            "value": f"{num_images}Hãy tổng hợp toàn bộ nội dung đề thi dưới dạng JSON với cấu trúc hoàn chỉnh bao gồm:\n"
                    "1. Tất cả các sections với đầy đủ thông tin\n"
                    "2. Toàn bộ câu hỏi trong từng section\n"
                    "3. Các metadata quan trọng\n"
                    "Yêu cầu định dạng JSON rõ ràng, đầy đủ và có cấu trúc phân cấp hợp lý."
        })
        new_conversations.append({
            "from": "gpt", 
            "value": final_response
        })

        # Combine data
        final_data = original_data
        final_data["conversations"] = new_conversations
        processed_data.append(final_data)

# Write output
with open(output_file, "w", encoding="utf-8") as file:
    for obj in processed_data:
        file.write(json.dumps(obj, ensure_ascii=False, indent=4) + "\n")

print(f"Đã xử lý {len(processed_data)} JSON và ghi vào {output_file}.")
