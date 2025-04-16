import asyncio
from aioconsole import ainput, aprint
import aiohttp
import aiofiles
import os


async def download_image(url, save_path: str) -> bool:
  try:
    filename = os.path.basename(url)

    if save_path is None:
      save_path = filename
    else:
      if os.path.isdir(save_path):
        save_path = os.path.join(save_path, filename)

      async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
          if response.status != 200:
            raise Exception(f"HTTP Error: {response.status}")

          async with aiofiles.open(save_path, 'wb') as file:
            await file.write(await response.read())

    return True

  except Exception as e:
    return False


async def get_valid_directory():
  while True:
    user_input = (await ainput()).strip()

    if not user_input:
      return os.getcwd()

    if os.path.isdir(user_input):
      return os.path.abspath(user_input)
    else:
      await aprint(
          f"Ошибка: директории '{user_input}' не существует. Попробуйте снова.")


async def print_results(results):
  max_url_length = max(
      len(url) for item in results for url in item.keys()) if results else 0
  max_url_length = min(max_url_length, 57)

  header_line = "+" + "-" * (max_url_length + 2) + "+" + "-" * 8 + "+"
  await aprint(header_line)
  await aprint(f"| {'Ссылка'.ljust(max_url_length)} | Статус |")
  await aprint(header_line)

  for item in results:
    for url, status in item.items():
      truncated_url = (url[:54] + '...') if len(url) > 57 else url
      status_text = 'Успех' if status else 'Ошибка'
      await aprint(
          f"| {truncated_url.ljust(max_url_length)} | {status_text.ljust(6)} |")

  await aprint(header_line)


async def main():
  try:
    save_dir: str = await get_valid_directory()
    tasks = []
    results = []

    while True:
      try:
        url = (await ainput()).strip()
        if not url:
          break

        task = asyncio.create_task(download_image(url, save_dir))
        tasks.append((url, task))

      except KeyboardInterrupt:
        break

    for url, task in tasks:
      try:
        result = await task
        results.append({url: result})
      except Exception as e:
        results.append({url: False})

    await print_results(results)

  except KeyboardInterrupt:
    await aprint("\nЗавершение по запросу пользователя...")
  except Exception as e:
    await aprint(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    pass
