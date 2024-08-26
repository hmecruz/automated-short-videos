import asyncio
import json
import os
import sys

from Exceptions import DurationExceededError
from Logger import Logger
from Quiz import Quiz
from WYR import WYR


def main():

    if len(sys.argv) != 2:
        print(
            f"Number of arguments incorrect!\nUsage example: python {sys.argv[0]} <input_file_path>"
        )
        sys.exit(1)

    input_file_path = sys.argv[1]  # JSON File with info

    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("quiz", exist_ok=True)
    os.makedirs(os.path.join("quiz", "all_quizzes"), exist_ok=True)
    os.makedirs("wyr", exist_ok=True)
    os.makedirs(os.path.join("wyr", "all_wyr"), exist_ok=True)

    all_quizzes_dir = os.path.join("quiz", "all_quizzes")
    all_wyr_dir = os.path.join("wyr", "all_wyr")

    logger = Logger("logs")

    # Read the input file
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            input_file = json.load(file)
    except FileNotFoundError:
        print(f"Input file '{input_file_path}' not found.")
        logger.log_error(f"Input file '{input_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Input file '{input_file_path}' is not a valid JSON file.")
        logger.log_error(f"Input file '{input_file_path}' is not a valid JSON file.")
        sys.exit(1)

    # Process JSON file data
    for data in input_file:
        name = data.get("name")
        content = data.get("content")

        if not name or not content:
            print(f"Invalid quiz data: {data}")
            logger.log_error(f"Invalid quiz data: {data}")
            continue

        if "quiz" in name:

            lines_en = content.get("en", [])
            lines_pt = content.get("pt", [])

            quiz_dir = os.path.join("quiz", name)
            os.makedirs(quiz_dir, exist_ok=True)

            quiz = Quiz()

            # English Quiz
            try:
                asyncio.run(
                    quiz.process_quiz(name, lines_en, "en", quiz_dir, [all_quizzes_dir])
                )
            except DurationExceededError as e:
                logger.log_error(f"Warning processing {name} in English: {e}")
            except ValueError as e:
                logger.log_error(f"Error processing {name} in English: {e}")

            # Portuguese Quiz
            try:
                asyncio.run(
                    quiz.process_quiz(name, lines_pt, "pt", quiz_dir, [all_quizzes_dir])
                )
            except DurationExceededError as e:
                logger.log_error(f"Warning processing {name} in Portuguese: {e}")
            except ValueError as e:
                logger.log_error(f"Error processing {name} in Portuguese: {e}")

        elif "wyr" in name:

            lines_en = content.get("en", [])
            lines_pt = content.get("pt", [])

            # Ensure there is an even number of lines for both languages
            if len(lines_en) % 2 != 0 or len(lines_pt) % 2 != 0:
                logger.log_error(
                    f"Odd number of lines in WYR data for {name}. Lines should be even."
                )
                continue

            # Concatenate lines
            concatenated_lines_en = [
                f"{lines_en[i]}, or {lines_en[i+1]}" for i in range(0, len(lines_en), 2)
            ]
            concatenated_lines_pt = [
                f"{lines_pt[i]}, ou {lines_pt[i+1]}" for i in range(0, len(lines_pt), 2)
            ]

            wyr_dir = os.path.join("wyr", name)
            os.makedirs(wyr_dir, exist_ok=True)

            wyr = WYR()

            # English Quiz
            try:
                asyncio.run(
                    wyr.process_wyr(
                        name, concatenated_lines_en, "en", wyr_dir, [all_wyr_dir]
                    )
                )
            except DurationExceededError as e:
                logger.log_error(f"Warning processing {name} in English: {e}")
            except Exception as e:
                logger.log_error(f"Error processing {name} in English: {e}")

            # Portuguese Quiz
            try:
                asyncio.run(
                    wyr.process_wyr(
                        name, concatenated_lines_pt, "pt", wyr_dir, [all_wyr_dir]
                    )
                )
            except DurationExceededError as e:
                logger.log_error(f"Warning processing {name} in Portuguese: {e}")
            except Exception as e:
                logger.log_error(f"Error processing {name} in Portuguese: {e}")

        else:
            print(f"Unexpected quiz name format: {name}")
            logger.log_error(f"Unexpected quiz name format: {name}")
            continue


if __name__ == "__main__":
    main()
