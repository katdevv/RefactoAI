import json
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Read environment
DB_PATH = os.getenv("DATABASE_PATH")
JSON_FILE_PATH = os.getenv("JSON_FILE_PATH")

if not DB_PATH:
    raise RuntimeError("DATABASE_PATH not set in .env")
if not JSON_FILE_PATH:
    raise RuntimeError("JSON_FILE_PATH not set in .env")


class TaskType:
    def __init__(self, id: int, name: str, description: str, topic: str, correct_code: str, messed_code: str):
        self.id = id
        self.name = name
        self.description = description
        self.topic = topic
        self.correct_code = correct_code
        self.messed_code = messed_code

class InputRow:
    def __init__(self, id: int, input: str, input_type: str, input_output_id: int):
        self.id = id
        self.input = input
        self.input_type = input_type
        self.input_output_id = input_output_id


def get_json_data(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading JSON: {e}")
        return []


def get_task_insert(task: TaskType):
    sql = """
        INSERT INTO tasks (id, name, description, topic, correct_code, messed_code)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (task.id, task.name, task.description, task.topic, task.correct_code, task.messed_code)
    return sql, params


def get_input_insert(inp: InputRow):
    sql = """
        INSERT INTO input (id, input, input_type, input_output_id)
        VALUES (?, ?, ?, ?)
    """
    params = (inp.id, inp.input, inp.input_type, inp.input_output_id)
    return sql, params


def add_data_to_db(table: str = "tasks"):
    print("Establishing database connection")
    conn = None
    try:
        db_path = Path(DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        print(f"Loading JSON from {JSON_FILE_PATH}")
        data = get_json_data(JSON_FILE_PATH)
        if not isinstance(data, list) or not data:
            print("No records found in JSON; nothing to insert.")
            return

        if table == "tasks":
            print("Inserting tasks ...")
            for row in data:
                task = TaskType(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    topic=row["topic"],
                    correct_code=row["correct_code"],
                    messed_code=row["messed_code"],
                )
                sql, params = get_task_insert(task)
                cursor.execute(sql, params)

        elif table == "input":
            print("Inserting inputs ...")
            for row in data:
                inp = InputRow(
                    id=row["id"],
                    input=row["input"],
                    input_type=row["input_type"],
                    input_output_id=row["input_output_id"],
                )
                sql, params = get_input_insert(inp)
                cursor.execute(sql, params)
        else:
            raise ValueError(f"Unsupported table: {table}")

        conn.commit()
        print("Insert complete.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed")


if __name__ == "__main__":
    add_data_to_db("tasks")
