import random
import threading

PHI = 1.618033988749895


class Student:

  def __init__(self, name: str, gender: str, status: int):
    self.name: str = name
    self.gender: str = gender
    self.status: int = status
    self.answers: list[list[str]] = []
    self.__lock: threading.Lock = threading.Lock()

  def set_status(self, new_status: int):
    with self.__lock:
      self.status = new_status

  def get_status(self):
    with self.__lock:
      return self.status

  def processing_exam(self, questions: list[list[str]]):
    self.answers = []

    # Проверяем, что вопросов достаточно
    if len(questions) < 3:
      raise ValueError("В банке должно быть минимум 3 вопроса")

    # Выбираем 3 уникальных вопроса
    selected_question_indices = random.sample(range(len(questions)), 3)

    for q_idx in selected_question_indices:
      question = questions[q_idx]
      words = question.split()
      if not words:
        continue  # Пропускаем пустые вопросы

      selected_word = self._select_word(words)
      self.answers.append([selected_word, q_idx])

  def _select_word(self, words: list[str]) -> str:
    n = len(words)
    if n == 1:
      return words[0]

    # Создаем распределение вероятностей
    probabilities = []
    remaining_prob = 1.0

    for i in range(n):
      if i == n - 1:
        prob = remaining_prob
      else:
        prob = remaining_prob / PHI
        remaining_prob -= prob
      probabilities.append(prob)

    # Для девочек переворачиваем порядок вероятностей
    if self.gender == "Ж":
      probabilities = probabilities[::-1]

    # Выбираем слово согласно вероятностям
    rand = random.random()
    cumulative_prob = 0
    for i, prob in enumerate(probabilities):
      cumulative_prob += prob
      if rand <= cumulative_prob:
        return words[i]
    return words[-1]
