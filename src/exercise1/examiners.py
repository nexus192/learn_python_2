import random
import time
import threading
from enum import Enum

PHI = 1.618033988749895


class Mood(Enum):
  Neutral = 0
  Bad = 1
  Good = 2


class Examiner:

  def __init__(self, name: str, questions: list[str]):
    self.name: str = name
    self.total_students: int = 0
    self.current_student: str | None = None
    self.failed: int = 0
    self.working_time: float = 0.0
    self.questions: list[str] = questions
    self.question_stats = {question: 0 for question in questions}
    self.current_exam_start: int = 0
    self.__right_ans: list[list[str]] = []
    self.__mood: Mood = self._set_mood()
    self.__is_on_break: bool = False
    self.__lock = threading.Lock()
    self.GeneratingAnswers()

  @property
  def is_on_break(self):
    return self.__is_on_break

  @property
  def lock(self) -> threading.Lock:
    return self.__lock

  @lock.setter
  def lock(self, lock: threading.Lock):
    self.__lock = lock

  def get_current_state(self):
    with self.lock:
      current_time = time.time()
      if self.current_student:
        total_working = self.working_time + (current_time -
                                             self.current_exam_start)
      else:
        total_working = self.working_time

      return {
          'name': self.name,
          'current_student': self.current_student,
          'total_students': self.total_students,
          'failed': self.failed,
          'working_time': total_working
      }

  def _set_mood(self) -> Mood:
    mood_prob = random.random()
    if mood_prob < 1 / 8:
      return Mood.Bad
    elif mood_prob < 1 / 8 + 1 / 4:
      return Mood.Good
    return Mood.Neutral

  def GeneratingAnswers(self):
    self.__right_ans = []
    for question in self.questions:
      words = question.split()
      if not words:
        self.__right_ans.append([])
        continue

      selected_words = []
      remaining_words = words.copy()

      if remaining_words:
        idx = self._select_word_index(len(remaining_words))
        selected_words.append(remaining_words.pop(idx))

      while remaining_words and random.random() < 1 / 3:
        idx = self._select_word_index(len(remaining_words))
        selected_words.append(remaining_words.pop(idx))

      self.__right_ans.append(selected_words)

  def _select_word_index(self, num_words: int) -> int:
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

  def evaluate_answers(self, student) -> bool:
    if self.__mood == Mood.Good:
      # Все ответы считаем правильными
      for q_idx in range(len(self.questions)):
        question = self.questions[q_idx]
        self.question_stats[question] += 1
      return True
    elif self.__mood == Mood.Bad:
      # Все ответы считаем неправильными
      return False

    correct = 0
    for answer in student.answers:
      word, q_idx = answer
      question = self.questions[q_idx]
      if word in self.__right_ans[q_idx]:
        correct += 1
        self.question_stats[
            question] += 1  # Увеличиваем счетчик правильных ответов

    return correct > (len(student.answers)) - correct
