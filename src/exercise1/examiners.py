import random
import time
import threading
from enum import Enum

PHI = 1.618033988749895  # Золотое сечение


class Mood(Enum):
  Neutral = 0
  Bad = 1
  Good = 2


class Examiner:

  def __init__(self, name, questions):
    self.name = name
    self.questions = questions
    self.mood = self._set_mood()
    self.current_student = None
    self.total_students = 0
    self.failed = 0
    self.working_time = 0.0
    self.right_ans = []
    self.is_on_break = False
    self.lock = threading.Lock()
    self.start_time = time.time()
    self.GeneratingAnswers(questions)
    self.exam_duration = random.uniform(5, 7)  # Базовое время экзамена
    self.lock = threading.Lock()

  def get_current_state(self):
    with self.lock:
      return {
          'name': self.name,
          'current_student': self.current_student,
          'total_students': self.total_students,
          'failed': self.failed,
          'working_time': self.working_time
      }

  def _set_mood(self):
    mood_prob = random.random()
    if mood_prob < 1 / 8:
      return Mood.Bad
    elif mood_prob < 1 / 8 + 1 / 4:
      return Mood.Good
    return Mood.Neutral

  def GeneratingAnswers(self, questions):
    self.right_ans = []
    for question in questions:
      words = question.split()
      if not words:
        self.right_ans.append([])
        continue

      selected_words = []
      remaining_words = words.copy()

      if remaining_words:
        idx = self._select_word_index(len(remaining_words))
        selected_words.append(remaining_words.pop(idx))

      while remaining_words and random.random() < 1 / 3:
        idx = self._select_word_index(len(remaining_words))
        selected_words.append(remaining_words.pop(idx))

      self.right_ans.append(selected_words)

  def _select_word_index(self, num_words):
    if num_words == 1:
      return 0

    probabilities = []
    remaining_prob = 1.0

    for i in range(num_words):
      if i == num_words - 1:
        prob = remaining_prob
      else:
        prob = remaining_prob / PHI
        remaining_prob -= prob
      probabilities.append(prob)

    rand = random.random()
    cumulative_prob = 0
    for i, prob in enumerate(probabilities):
      cumulative_prob += prob
      if rand <= cumulative_prob:
        return i
    return num_words - 1

  def take_exam(self, student):
    with self.lock:
      self.current_student = student.name
      self.total_students += 1

    # Студент сдает экзамен
    student.take_exam(self.questions)

    # Проверяем ответы
    passed = self.evaluate_answers(student)

    # Обновляем статус студента
    student.status = 1 if passed else 2
    if not passed:
      with self.lock:
        self.failed += 1

    # Время экзамена зависит от длины имени экзаменатора
    exam_time = self.exam_duration * len(
        self.name) / 6  # Нормализуем к длине "Степан" (6 букв)
    time.sleep(exam_time)

    with self.lock:
      self.working_time += exam_time
      self.current_student = None

  def evaluate_answers(self, student):
    # Проверяем настроение
    if self.mood == Mood.Good:
      return True
    elif self.mood == Mood.Bad:
      return False

    # Нейтральное настроение - объективная проверка
    correct = 0
    total = 0

    for answer in student.answers:
      word, q_idx = answer
      if word in self.right_ans[q_idx]:
        correct += 1
      total += 1

    return correct > (total - correct)

  def work(self):
    while True:
      # Проверяем, не пора ли на обед
      elapsed = time.time() - self.start_time
      if elapsed >= 30 and not self.is_on_break:
        self.is_on_break = True
        # Завершаем текущего студента
        if self.current_student:
          time.sleep(1)  # Даем закончить текущему
        # Обеденный перерыв
        break_time = random.uniform(12, 18)
        time.sleep(break_time)
        self.is_on_break = False
        self.start_time = time.time()  # Сбрасываем таймер
        self.mood = self._set_mood()  # Может измениться настроение
