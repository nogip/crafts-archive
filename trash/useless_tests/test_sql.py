import sqlite3
from  modules.ege_parser.Problem import Problem


def init(conn):
    crs = conn.cursor()
    tables = \
    """
    PRAGMA foreign_keys = off;
    BEGIN TRANSACTION;
    
    CREATE TABLE IF NOT EXISTS Problem (theme_name INTEGER REFERENCES Theme (name), id INTEGER, text TEXT, solve TEXT, help TEXT, images BLOB);
    
    CREATE TABLE IF NOT EXISTS Subject (name STRING PRIMARY KEY UNIQUE);
    
    CREATE TABLE IF NOT EXISTS Task (subject_name STRING REFERENCES Subject (name), name STRING PRIMARY KEY);
    
    CREATE TABLE IF NOT EXISTS Theme (task_name STRING REFERENCES Task (name), name STRING PRIMARY KEY);
    
    COMMIT TRANSACTION;
    PRAGMA foreign_keys = on;

    """
    crs.executescript(tables)

def get_task_list(conn, subject):
    input_tasks = get(conn, subject, depth=1)
    tasks = [task[1] for task in input_tasks]
    return tasks

def get_themes_list(conn, subject):
    input_themes = get(conn, subject,  depth=2)
    themes_list = [theme[1] for theme in input_themes]
    return themes_list

def get(connection, subject, task=None, theme=None, depth=3):
    if depth > 3:
        depth = 3
    levels = {
        1: 'Task',
        2: 'Theme',
        3: 'Problem'
    }
    crs = connection.cursor()

    def format_arg(arg, ):
        if isinstance(arg, int):
            return arg
        return "'{}'".format(arg)

    execute = \
        """
    SELECT DISTINCT {level}.*
    FROM Subject, Task, Theme, Problem
    WHERE
        Subject.name = '{subject}' AND
        Task.subject_name = Subject.name AND
        Theme.task_name = {task} AND
        Problem.theme_name = {theme}
    """.format(
            level=levels.get(depth),
            subject=subject if subject else '*',
            task=format_arg(task) if task else 'Task.name',
            theme=format_arg(theme) if theme else 'Theme.name'
        )
    crs.execute(execute)
    return crs.fetchall()

def convert_to_objects(prob_tuples):
    problems = []
    for problem in prob_tuples:
        theme_name = problem[0]
        prob_id = problem[1]
        text = problem[2]
        solve = problem[3]
        help = problem[4]
        images = problem[5]
        problem = Problem(theme_name, prob_id, text, solve, help, images)
        problems.append(problem)
    return problems


def add(conn, subject):
    pass


if __name__ == '__main__':
    conn = sqlite3.connect('EGE_DB.db')
    init(conn)
    res = convert_to_objects(get(conn, 'math'))
    # for row in res:
    #     print(row)

    print(get_themes_list(conn, 'rus'))
    print(get(conn, 'rus', depth=1))