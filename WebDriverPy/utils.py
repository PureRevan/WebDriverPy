from typing import Callable, Any
from functools import wraps

from random import choices

from shutil import move, rmtree, Error as ShutilError
from os import remove, listdir, makedirs
from os.path import exists, join, splitext, abspath, isfile, dirname, basename
from zipfile import ZipFile


def ensure_exists(dir_name: str) -> str:
    makedirs(dir_name, exist_ok=True)
    return dir_name


def resolve_resource_path(resource_name: str,
                          make_sure_exists: bool = True) -> str:
    """
    Resolve a relative path to an absolute one using the package root directory as a reference (e.g. "." -> package root directory)
    :param resource_name: The relative path to the resource to resolve (e.g. "./logs/driver_logs.txt")
    :param make_sure_exists: Whether to ensure the directory to this resource exists.
        This does not create a file, if the file does not exist. It will, however, create the directories pathing to that file
    :return: Returns the absolute path to that resource
    """
    resource_path = abspath(join(dirname(__file__), resource_name))

    if make_sure_exists:
        ensure_exists(dirname(resource_path))

    return str(resource_path)


def extract_from_zip(
        zip_file_path: str,
        file_to_extract: str,
        output_dir: str = resolve_resource_path("."),
        temp_dir: str = resolve_resource_path("./temp"),
        inner_extraction_dir: str | None = None,
        log_func: Callable[[str, str], Any] = lambda _: None) -> str:

    with ZipFile(zip_file_path, "r") as zip_ref:
        start_dir = list({x.split("/", maxsplit=1)[0] for x in zip_ref.namelist()})

        if start_dir and inner_extraction_dir is None:
            inner_extraction_dir = start_dir[0] if len(start_dir) == 1 else basename(splitext(zip_file_path)[0])

        zip_ref.extract(
            f"{inner_extraction_dir}\\{file_to_extract}".lstrip('.\\').replace("\\", "/"),
            path=temp_dir
        )

    move(join(temp_dir, inner_extraction_dir, file_to_extract), output_dir)
    remove(zip_file_path)

    # Try to remove remnants of extraction (expected to be empty)
    try:
        rmtree(join(temp_dir, inner_extraction_dir))
    except ShutilError as e:
        log_func(f"Failed to remove directory expected to be empty: {inner_extraction_dir}\n"
                 f"Short Description: {str(e)}", "WARNING")

    return abspath(join(output_dir, file_to_extract))


def extract_all_from_zip(
        zip_file_path: str,
        output_dir: str | None = None,
        inner_extraction_dir: str | None = None,
        temp_dir: str = resolve_resource_path("./temp"),
        log_func: Callable[[str, str], Any] = lambda _: None) -> str:
    if output_dir is None:
        output_dir = inner_extraction_dir

    with ZipFile(zip_file_path, "r") as zip_ref:
        start_dir = list({x.split("/", maxsplit=1)[0] for x in zip_ref.namelist()})

        if start_dir and inner_extraction_dir is None:
            inner_extraction_dir = start_dir[0] if len(start_dir) == 1 else basename(splitext(zip_file_path)[0])

        zip_ref.extractall(temp_dir)
    remove(zip_file_path)

    if output_dir != inner_extraction_dir:
        temp_extraction_dir = join(temp_dir, inner_extraction_dir)
        move_all_files(temp_extraction_dir, output_dir)

        # Try to remove remnants of extraction (expected to be empty)
        try:
            rmtree(temp_extraction_dir)
        except ShutilError as e:
            log_func(f"Failed to remove directory expected to be empty: {temp_extraction_dir}\n"
                     f"Short Description: {str(e)}", "WARNING")

    return abspath(output_dir)


def force_delete(target: str, force_non_empty_dir_deletion: bool = True):
    if isfile(target):
        remove(target)
    else:
        rmtree(target, ignore_errors=force_non_empty_dir_deletion)


def check_file_exists(file: str, check_dir: str = ".") -> bool:
    return isfile(join(check_dir, file))


def move_all_files(src_dir: str, dest_dir: str) -> None:
    for file in listdir(src_dir):
        move(join(src_dir, file), dest_dir)


def read_content(file_path: str) -> str:
    with open(file_path, "r") as file:
        content = file.read()
    return content


def read_template_content(file_path: str, template_identifier_to_value: dict[str, str]) -> str:
    content = read_content(file_path)

    for old, new in template_identifier_to_value.items():
        content = content.replace(old, new)

    return content


def dump(data: str, file: str, mode: str = "a") -> None:
    if not exists(file):
        open(file, "x").close()

    with open(file, mode) as file:
        file.write(data)


def saves_to_file(file: str | Callable[[], str], f: Callable[[Any, ...], str], write_mode: str = "a") \
        -> Callable[[Any, ...], None]:
    if isinstance(file, str) and not exists(file):
        open(file, "x").close()

    @wraps(f)
    def wrapper(*args, **kwargs) -> None:
        with open(file if isinstance(file, str) else file(), write_mode) as output_file:
            output_file.write(f(*args, **kwargs))

    return wrapper


def file_name_gen(base_name: str, path: str = ".", do_not_use: list[str] = None) -> str:
    if do_not_use is None:
        do_not_use = []

    i = 1
    current = join(path, base_name)
    base, ext = splitext(base_name)

    while exists(current) or current in do_not_use:
        current = join(path, f"{base}_{i}{ext}")
        i += 1

    return abspath(current)


def find_files_with_extension(directory: str, extension: str) -> list[str]:
    found = []

    for file in listdir(directory):
        if splitext(file)[1] == extension:
            found.append(join(directory, file))

    return found


def rand_text_split(text: str) -> list[str]:
    group_sizes = [1, 2, 3]
    weights = [3, 3, 2]

    result = []
    i = 0

    while i < len(text):
        group_size = choices(group_sizes, weights)[0]
        group = text[i:i + group_size]
        result.append(group)
        i += group_size

    return result


def is_authenticated_proxy_string(proxy_string: str) -> bool:
    return proxy_string.count(":") > (2 if "://" in proxy_string else 1)


def clear_files(directory: str, condition: Callable[[str], bool] = lambda _: True) -> None:
    for element in listdir(directory):
        if isfile(element) and condition(element):
            remove(element)

