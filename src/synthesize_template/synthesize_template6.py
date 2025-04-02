import os
import random 
import re

def modify_string(input_string):
    # Regex to match the pattern 'Câu {n}.' or 'Câu {n}:'
    pattern = r'(Câu (\d{1,2})[\.:])'
    
    # Function to replace matched pattern
    def replace_match(match):
        # Add <question> and <indicator> tags around the pattern
        return f'<question><indicator> {match.group(1)}<indicator\>'

    # Apply regex substitution to the string
    modified_string = re.sub(pattern, replace_match, input_string)
    
    return modified_string

questions_folder = './questions_v1'
answers_folder = './answers_v1'
solutions_folder = './solutions_v1' 
output_folder_1 = './Template6(partialsol[...]partialsol)/synthesize_input'
output_folder_2 = './Template6(partialsol[...]partialsol)/synthesize_output'

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

def extract_partial(question):
    '''This function splits the question into a partial beginning and partial ending with random word counts'''
    words = question.split()
    
    num_beginning_words = random.randint(6, 15)  
    num_ending_words = random.randint(6, 15)     
    
    partial_beginning = ' '.join(words[:min(num_beginning_words, len(words))])
    partial_ending = ' '.join(words[-min(num_ending_words, len(words)):])
    
    return partial_beginning, partial_ending


def create_combined_mmd_files(questions, answers, solutions, output_folder_1, output_folder_2):
    """
    Creates 1000 .mmd files, each containing 3 or 4 randomly chosen questions
    followed by randomly chosen answers and solutions for each question.
    """
    num_questions = len(questions)
    total_files = 1000  

    file_index = 1
    created_files = 0  

    while created_files < total_files:
        output_file_1 = os.path.join(output_folder_1, f'combined_{file_index:04d}.mmd')
        output_file_2 = os.path.join(output_folder_2, f'combined_{file_index:04d}.mmd')

        ans_list = []
        sol_list = []
        
        # Randomly choose 3 or 4 questions for the current file
        num_questions_in_file = random.choice([3, 4, 5])
        
        # Randomly select the questions for this file
        selected_questions_indices = random.sample(range(num_questions), num_questions_in_file)

        
        with open(output_file_1, 'w', encoding='utf-8') as f:
            j = 0
            for i in selected_questions_indices:
                if j==0:
                    solution = random.choice(solutions)
                    _, partial_ending = extract_partial(solution)
                    ending_cache = partial_ending 

                    f.write(f"{partial_ending}\n")
                    f.write("\n")
                elif j == len(selected_questions_indices) - 1:
                    solution = random.choice(solutions)
                    partial_beginning, _ = extract_partial(solution)
                    beginning_cache = partial_beginning

                    f.write(f"{partial_beginning}\n")
                    f.write("\n")
                else:
                    f.write(f"{questions[i]}\n")
                    f.write("\n")
                
                    answer = random.choice(answers)
                    ans_list.append(answer)

                    solution = random.choice(solutions)
                    sol_list.append(solution)

                    f.write(f"{answer}\n")
                    f.write("\n")
                    f.write(f"{solution}\n")
                    f.write("\n")
                j += 1
            
        print(f"Created file: {output_file_1}")
        
        
        with open(output_file_2, 'w', encoding='utf-8') as f:
            j = 0
            k = 0
            for i in selected_questions_indices:
                if j==0:
                    f.write(f"<question><solution> {ending_cache} <solution\><question\>\n")
                    f.write("\n")
                elif j == len(selected_questions_indices) - 1:
                    f.write(f"<solution>{beginning_cache} <solution\><question\>\n")
                    f.write("\n")
                else:
                    question_with_head = modify_string(questions[i])
                    f.write(f"{question_with_head}\n")
                    f.write("\n")

                    f.write(f"<choices> {ans_list[k]} <choices\>\n")
                    f.write("\n")
                    
                    f.write(f"<solution> {sol_list[k]} <solution\><question\>\n")
                    f.write("\n")
                    k += 1
                j += 1
        
        print(f"Created file: {output_file_2}")
        file_index += 1
        created_files += 1


question_content = read_mmd_files(questions_folder)
answer_content = read_mmd_files(answers_folder)
solution_content = read_mmd_files(solutions_folder)

questions = extract_sections(question_content)
answers = extract_sections(answer_content)
solutions = extract_sections(solution_content)

create_combined_mmd_files(questions, answers, solutions, output_folder_1, output_folder_2)

