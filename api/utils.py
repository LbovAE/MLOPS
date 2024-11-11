import pandas as pd
from dvc.repo import Repo


def push_file_to_dvc(data: dict, data_name: str):
    """

    Загружает данные в репозиторий DVC (Data Version Control).

    Аргументы:
        data (dict): Словарь, содержащий данные, которые нужно загрузить в репозиторий DVC,
                     где ключи представляют названия столбцов, и значения представляют сами данные для каждого столбца.
        data_name (str): Название файла данных, которое будет создано в репозитории DVC.

    """

    df = pd.DataFrame(data)
    repo = Repo()

    data_filename = f"data/{data_name}.csv"
    df.to_csv(data_filename, index=False)

    repo.add(data_filename)
    repo.push()
