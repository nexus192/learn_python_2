from queue import Queue, Empty
from collections import namedtuple
import curses
import time
import threading
import examiners
import students

LoadInfoResult = namedtuple("LoadInfoResult", [
    "examiners", 
    "students_list", 
    "students_queue", 
    "questions"
])

def load_data(file_path: str) -> list[str]:
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      return [line.strip() for line in f if line.strip()]
  except FileNotFoundError as e:
        raise FileNotFoundError(f"Файл {file_path} не найден") from e
  except OSError as e:
        raise OSError(f"Ошибка при чтении файла {file_path}: {str(e)}") from e

def load_info() -> LoadInfoResult:
  examiners_names = load_data(
      "/home/nexus/Desktop/s21_project/AP1-Py/TO2/learn_python_2/src/exercise1/input/examiners.txt"
  )
  students_data = load_data(
      "/home/nexus/Desktop/s21_project/AP1-Py/TO2/learn_python_2/src/exercise1/input/students.txt"
  )
  questions = load_data(
      "/home/nexus/Desktop/s21_project/AP1-Py/TO2/learn_python_2/src/exercise1/input/questions.txt"
  )

  # Парсинг данных студентов
  students_list = []
  students_queue = Queue()
  for line in students_data:
    parts = line.split()
    if len(parts) >= 2:  # Минимум имя и пол
      name = parts[0]
      gender = parts[1]
      status = int(parts[2]) if len(parts) > 2 else 0
      student = students.Student(name, gender, status)
      students_list.append(student)
      students_queue.put(student)

  # Создание экзаменаторов
  list_examiners = [
      examiners.Examiner(name, questions) for name in examiners_names
  ]

  return LoadInfoResult(list_examiners, students_list, students_queue, questions)

def draw_examiners_table(stdscr: curses.window, examiners: list[examiners.Examiner], start_line: int):
    stdscr.addstr(
        start_line, 0,
        "+-------------+-----------------+-----------------+---------+--------------+"
    )
    stdscr.addstr(
        start_line + 1, 0,
        "| Экзаменатор | Текущий студент | Всего студентов | Завалил | Время работы |"
    )
    stdscr.addstr(
        start_line + 2, 0,
        "+-------------+-----------------+-----------------+---------+--------------+"
    )

    for i, examiner in enumerate(examiners, start=3):
        state = examiner.get_current_state()
        name = state['name'][:11].ljust(11)
        current = state['current_student'][:15].ljust(15) if state['current_student'] else '-'.ljust(15)
        stdscr.addstr(
            start_line + i, 0,
            f"| {name} | {current} | {str(state['total_students']).ljust(15)} | {str(state['failed']).ljust(7)} | {f'{state["working_time"]:.1f}c'.ljust(12)} |"
        )

    stdscr.addstr(
        start_line + len(examiners) + 3, 0,
        "+-------------+-----------------+-----------------+---------+--------------+"
    )

def draw_students_table(stdscr: curses.window, students: list[students.Student], start_line: int):
    stdscr.addstr(start_line, 0, "+------------+----------+")
    stdscr.addstr(start_line + 1, 0, "| Студент    |  Статус  |")
    stdscr.addstr(start_line + 2, 0, "+------------+----------+")

    for i, student in enumerate(students, start=3):
        name = student.name[:10].ljust(10)
        status_text = {
            0: "Очередь",
            1: "Сдал",
            2: "Провалил"
        }.get(student.get_status(), "Неизвестно")
        stdscr.addstr(start_line + i, 0, f"| {name} | {status_text.center(8)} |")

    stdscr.addstr(start_line + len(students) + 3, 0, "+------------+----------+")
    return start_line + len(students) + 4

def take_exam(examiner: examiners.Examiner, student: students.Student):
  with examiner.lock:
    examiner.current_student = student.name
    examiner.total_students += 1
    examiner.current_exam_start = time.time()

  student.processing_exam(examiner.questions)

  passed = examiner.evaluate_answers(student)

  exam_time = examiner.exam_duration * len(examiner.name) / 6
  time.sleep(exam_time)

  with examiner.lock:
    student.status = 1 if passed else 2
    if not passed:
      examiner.failed += 1
    examiner.working_time += (time.time() - examiner.current_exam_start)
    examiner.current_student = None

def main(stdscr: curses.window):
  curses.curs_set(0)
  stdscr.nodelay(1)

  data = load_info()
  last_update = time.time()
  update_interval = 0.1

  try:
    while True:
      current_time = time.time()

      for examiner in data.examiners:
        if not examiner.is_on_break and examiner.current_student is None:
          try:
            student = data.students_queue.get_nowait()
            exam_thread = threading.Thread(target=take_exam,
                                           args=(examiner, student,), daemon=True)
            exam_thread.start()
          except Empty:
            pass

      if current_time - last_update >= update_interval:
        stdscr.clear()
        current_line = draw_students_table(stdscr, data.students_list, 0)
        draw_examiners_table(stdscr, data.examiners, current_line)
        stdscr.refresh()
        last_update = current_time

      time.sleep(0.01)

  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  curses.wrapper(main)
