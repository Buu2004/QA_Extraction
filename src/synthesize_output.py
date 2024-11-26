import os
import random 
import re

def modify_string(input_string):
    # Regex to match the pattern 'Câu {n}.' or 'Câu {n}:'
    pattern = r'(Câu (\d{1,2})[\.:])'
    
    # Function to replace matched pattern
    def replace_match(match):
        # Add <question> and <indicator> tags around the pattern
        return f'<question><indicator> {match.group(1)}<indicator\\>'

    # Apply regex substitution to the string
    modified_string = re.sub(pattern, replace_match, input_string)
    
    return modified_string

questions_folder = './questions'
answers_folder = './answers'
solutions_folder = './solutions'
output_folder = './synthesize_out'

def read_mmd_files(folder_path):
    """Reads all .mmd files in a given folder and returns the content."""
    mmd_files = [f for f in os.listdir(folder_path) if f.endswith('.mmd')]
    content = []
    for file in mmd_files:
        with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
            content.append(f.read())
    return content

def extract_sections(content, delimiter="<end\>"):
    """Extracts sections (questions, answers, solutions) from content separated by the delimiter."""
    sections = []
    for item in content:
        parts = item.split(delimiter)
        sections.extend([part.strip() for part in parts if part.strip()])
    return sections

def create_combined_mmd_files(questions, answers, solutions, output_folder):
    """
    Creates multiple .mmd files with either 3 or 4 randomly chosen questions in each file,
    followed by a randomly chosen answer and solution for each question.
    """
    num_questions = len(questions)
    file_index = 1

    while file_index <= (num_questions // 3) + 1:
        output_file = os.path.join(output_folder, f'combined_{file_index:03d}.mmd')
        
        num_questions_in_file = random.choice([3, 4])
        start_index = (file_index - 1) * 4
        end_index = start_index + num_questions_in_file

        end_index = min(end_index, num_questions)

        if start_index >= num_questions:
            # If there are no questions left to process, break out of the loop
            break

        # Only create the file if there are questions to write
        with open(output_file, 'w', encoding='utf-8') as f:
            for i in range(start_index, end_index):
                question_with_head = modify_string(questions[i])
                f.write(f"{question_with_head}\n")
                f.write("\n")
                
                # Randomly choose an answer and solution
                answer = random.choice(answers)
                solution = random.choice(solutions)
                
                f.write(f"<choices> {answer} <choices/>\n")
                f.write("\n")
                f.write(f"<solution> {solution} <solution/>\n")
                f.write("\n")
        
        print(f"Created file: {output_file}")
        file_index += 1

question_content = read_mmd_files(questions_folder)
answer_content = read_mmd_files(answers_folder)
solution_content = read_mmd_files(solutions_folder)

questions = extract_sections(question_content)
answers = extract_sections(answer_content)
solutions = extract_sections(solution_content)

create_combined_mmd_files(questions, answers, solutions, output_folder)

