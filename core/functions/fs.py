import shutil
from pathlib import Path

from core.decorator.function_decorator import markus_function

@markus_function
def read_file(file_path: str) -> str:
    """
    Lire le contenu d'un fichier.

    Args:
        file_path (str): Chemin vers le fichier.

    Returns:
        str: Contenu du fichier en UTF-8.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text(encoding="utf-8")


@markus_function
def write_file(file_path: str, content: str, overwrite: bool = True):
    """
    Écrire du contenu dans un fichier.

    Args:
        file_path (str): Chemin du fichier à créer ou écraser.
        content (str): Contenu à écrire.
        overwrite (bool, optional): Écraser le fichier s'il existe. Default is True.

    Raises:
        FileExistsError: Si le fichier existe et overwrite=False.
    """
    path = Path(file_path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {file_path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@markus_function
def create_file(file_path: str):
    """
    Créer un fichier vide.

    Args:
        file_path (str): Chemin du fichier à créer.

    Raises:
        FileExistsError: Si le fichier existe déjà.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        raise FileExistsError(f"File already exists: {file_path}")

    path.touch()


@markus_function
def delete_file(file_path: str):
    """
    Supprimer un fichier.

    Args:
        file_path (str): Chemin du fichier à supprimer.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    path.unlink()


@markus_function
def move_file(file_path: str, new_file_path: str):
    """
    Déplacer un fichier vers un nouveau chemin.

    Args:
        file_path (str): Chemin source.
        new_file_path (str): Nouveau chemin de destination.

    Raises:
        FileNotFoundError: Si le fichier source n'existe pas.
    """
    src = Path(file_path)
    dst = Path(new_file_path)

    if not src.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


@markus_function
def search_file(file_name: str, dir_path: str):
    """
    Chercher un fichier dans un répertoire récursivement.

    Args:
        file_name (str): Nom du fichier à chercher.
        dir_path (str): Répertoire racine de recherche.

    Returns:
        list[str]: Liste des chemins complets des fichiers trouvés.

    Raises:
        FileNotFoundError: Si le répertoire n'existe pas.
    """
    base = Path(dir_path)
    if not base.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    return [str(p) for p in base.rglob(file_name)]


@markus_function
def list_file(dir_path: str):
    """
    Lister tous les fichiers dans un répertoire (non récursif).

    Args:
        dir_path (str): Chemin du répertoire.

    Returns:
        list[str]: Liste des noms de fichiers.

    Raises:
        NotADirectoryError: Si le chemin n'est pas un répertoire.
    """
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    return [p.name for p in path.iterdir() if p.is_file()]

@markus_function
def create_dir(dir_path: str):
    """
    Créer un répertoire.

    Args:
        dir_path (str): Chemin du répertoire à créer.

    Raises:
        FileExistsError: Si le répertoire existe déjà.
    """
    path = Path(dir_path)
    if path.exists():
        raise FileExistsError(f"Directory already exists: {dir_path}")

    path.mkdir(parents=True)


@markus_function
def delete_dir(dir_path: str, recursive: bool = True):
    """
    Supprimer un répertoire.

    Args:
        dir_path (str): Chemin du répertoire.
        recursive (bool, optional): Supprimer récursivement le contenu. Default is True.

    Raises:
        NotADirectoryError: Si le chemin n'est pas un répertoire.
    """
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    if recursive:
        shutil.rmtree(path)
    else:
        path.rmdir()


@markus_function
def move_dir(dir_path: str, new_dir_path: str):
    """
    Déplacer un répertoire vers un nouveau chemin.

    Args:
        dir_path (str): Chemin source.
        new_dir_path (str): Chemin de destination.

    Raises:
        FileNotFoundError: Si le répertoire source n'existe pas.
    """
    src = Path(dir_path)
    dst = Path(new_dir_path)

    if not src.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    shutil.move(str(src), str(dst))


@markus_function
def list_dir(dir_path: str):
    """
    Lister le contenu d'un répertoire (fichiers et sous-répertoires).

    Args:
        dir_path (str): Chemin du répertoire.

    Returns:
        dict: {"dirs": [...], "files": [...]}

    Raises:
        NotADirectoryError: Si le chemin n'est pas un répertoire.
    """
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    return {
        "dirs": [p.name for p in path.iterdir() if p.is_dir()],
        "files": [p.name for p in path.iterdir() if p.is_file()],
    }


@markus_function
def base_dir() -> str:
    """
    Retourne le répertoire de travail courant absolu.

    Returns:
        str: Chemin absolu du dossier courant.
    """
    return str(Path().resolve())
