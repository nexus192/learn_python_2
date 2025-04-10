import examiners
import students
import curses
from queue import Queue, Empty
import time
import threading
import random


def load_data(file_path):
  """Загружает данные из файла и возвращает список строк."""
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      return [line.strip() for line in f if line.strip()]
  except FileNotFoundError:
    raise FileNotFoundError(f"Файл {file_path} не найден")
  except Exception as e:
    raise Exception(f"Ошибка при чтении файла {file_path}: {str(e)}")


def load_info():
  """Загружает все необходимые данные из файлов."""
  # Загрузка данных
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

  return list_examiners, students_list, students_queue, questions


def draw_examiners_table(stdscr, examiners, start_line):
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
    name = examiner.name[:11].ljust(11)
    current = examiner.current_student[:15].ljust(
        15) if examiner.current_student else '-'.ljust(15)
    stdscr.addstr(
        start_line + i, 0,
        f"| {name} | {current} | {str(examiner.total_students).ljust(15)} | {str(examiner.failed).ljust(7)} | {f'{examiner.working_time:.1f}c'.ljust(12)} |"
    )

  stdscr.addstr(
      start_line + len(examiners) + 3, 0,
      "+-------------+-----------------+-----------------+---------+--------------+"
  )


def draw_students_table(stdscr, students, start_line):
  stdscr.addstr(start_line, 0, "+------------+----------+")
  stdscr.addstr(start_line + 1, 0, "| Студент    |  Статус  |")
  stdscr.addstr(start_line + 2, 0, "+------------+----------+")

  for i, student in enumerate(students, start=3):
    name = student.name[:10].ljust(10)
    status_text = {
        0: "Очередь",
        1: "Сдал",
        2: "Провалил"
    }.get(student.status, "Неизвестно")
    stdscr.addstr(start_line + i, 0, f"| {name} | {status_text.center(8)} |")

  stdscr.addstr(start_line + len(students) + 3, 0, "+------------+----------+")
  return start_line + len(students) + 4


def main(stdscr):
  curses.curs_set(0)
  stdscr.nodelay(1)

  list_examiners, list_students, students_queue, questions = load_info()
  last_update = time.time()
  update_interval = 0.1  # 10 раз в секунду

  try:
    while True:
      current_time = time.time()

      # Распределяем студентов по свободным экзаменаторам
      for examiner in list_examiners:
        if not examiner.is_on_break and examiner.current_student is None:
          try:
            student = students_queue.get_nowait()
            # Создаем новый поток для каждого экзамена
            exam_thread = threading.Thread(target=examiner.take_exam,
                                           args=(student,))
            exam_thread.daemon = True  # Поток не будет мешать завершению программы
            exam_thread.start()
          except Empty:
            pass

      # Обновляем интерфейс с заданной частотой
      if current_time - last_update >= update_interval:
        stdscr.clear()
        current_line = draw_students_table(stdscr, list_students, 0)
        draw_examiners_table(stdscr, list_examiners, current_line)
        stdscr.refresh()
        last_update = current_time

      time.sleep(0.01)  # Короткая пауза для снижения нагрузки на CPU

  except KeyboardInterrupt:
    pass


if __name__ == "__main__":
  curses.wrapper(main)
