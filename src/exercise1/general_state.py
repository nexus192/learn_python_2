class GeneralState:

  def __init__(self, students_list):
    self.state_student: list[list[str, int, float]] = [[
        student.name, student.get_status(), 1000.0
    ] for student in students_list]
    self.best_examiners: list[str] = []
    self.best_students: list[str] = []
    self.best_questions: list[str] = []
    self.worst_students: list[str] = []
    self.remaining_students: int = len(students_list)
    self.total_exam_status: bool = False
    self.examiners_stats: dict[str, dict[str, int]] = {}
    self.questions_stats: dict[str, dict[str, int]] = {}

  def update_student(self, name: str, status: int, exam_time: float):
    for student in self.state_student:
      if student[0] == name:
        student[1] = status
        student[2] = exam_time
        break

  def update_examiner_stats(self, examiner_name, is_failed):
    if examiner_name not in self.examiners_stats:
      self.examiners_stats[examiner_name] = {'total': 0, 'failed': 0}
    self.examiners_stats[examiner_name]['total'] += 1
    if is_failed:
      self.examiners_stats[examiner_name]['failed'] += 1

  def update_question_stats(self, questions: list[str], examiners):
    question_stats = {question: 0 for question in questions}
    for examiner in examiners:
      for question, correct_count in examiner.question_stats.items():
        question_stats[question] += correct_count

      # Обновляем глобальную статистику
    for question, correct_count in question_stats.items():
      if question not in self.questions_stats:
        self.questions_stats[question] = {'total': 0, 'correct': 0}
      self.questions_stats[question]['correct'] += correct_count
      self.questions_stats[question]['total'] += examiner.total_students

  def find_best_students(self):
    passed_students = [s for s in self.state_student if s[1] == 1]
    if not passed_students:
      return ""
    min_time = min(s[2] for s in passed_students)
    best_students = [s[0] for s in passed_students if s[2] == min_time]
    self.best_students = best_students
    return ", ".join(best_students)

  def find_best_examiners(self):
    if not self.examiners_stats:
      return ""

    # Рассчитываем процент завалов для каждого экзаменатора
    examiner_success = []
    for name, stats in self.examiners_stats.items():
      if stats['total'] == 0:
        continue
      fail_percent = (stats['failed'] / stats['total']) * 100
      examiner_success.append((name, fail_percent))

    if not examiner_success:
      return ""

    # Находим экзаменаторов с наименьшим процентом завалов
    min_fail = min(fail for _, fail in examiner_success)
    best_examiners = [
        name for name, fail in examiner_success if fail == min_fail
    ]
    self.best_examiners = best_examiners
    return ", ".join(best_examiners)

  def find_worst_students(self):
    failed_students = [s for s in self.state_student if s[1] == 2]
    if not failed_students:
      return ""
    max_time = max(s[2] for s in failed_students)
    worst_students = [s[0] for s in failed_students if s[2] == max_time]
    self.worst_students = worst_students
    return ", ".join(worst_students)

  def find_best_questions(self):
    if not self.questions_stats:
      return ""

    # Рассчитываем процент правильных ответов для каждого вопроса
    question_success = []
    for question, stats in self.questions_stats.items():
      if stats['total'] == 0:
        continue
      success_percent = (stats['correct'] / stats['total']) * 100
      question_success.append((question, success_percent))

    if not question_success:
      return ""

    # Находим вопросы с наибольшим процентом правильных ответов
    max_success = max(success for _, success in question_success)
    best_questions = [q for q, s in question_success if s == max_success]
    self.best_questions = best_questions
    return ", ".join(best_questions)

  def find_total_exam_status(self):
    total_students = len(self.state_student)
    if total_students == 0:
      self.total_exam_status = False
      return "Экзамен не удался (нет студентов)"

    passed_students = sum(1 for s in self.state_student if s[1] == 1)
    pass_percentage = (passed_students / total_students) * 100
    self.total_exam_status = pass_percentage > 85
    return "Экзамен удался" if self.total_exam_status else "Экзамен не удался"
