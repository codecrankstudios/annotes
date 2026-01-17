import yaml
import glob
import os
from pathlib import Path
import settings
import datetime


# Loads the YAML configuration file
def load_config(config_path="config.yaml"):
    """
    Loads a YAML configuration file.

    Args:
        config_path (str or Path, optional): The path to the configuration file.
            Defaults to "config.yaml".

    Returns:
        dict or None: A dictionary representing the YAML content, or None if
        an error occurred.
    """
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return config_data
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{config_path}'")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None


# Reads all PDF files from the specified folder
def get_pdf_files(folder_path):
    """Get a list of all PDF files in the specified folder.

    Args:
        folder_path (str): Path to the folder containing PDF files.

    Returns:
        list: A list of PDF file paths.
    """
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    return pdf_files


def annotation_filename(pdf_basename):
    """
    Constructs the name and full path for an annotation file based on config.
    Supports placeholders: {date}, {time}, {pdf_name}, {pdf_stem}
    """
    # ensure pdf_basename does not include file extension
    pdf_stem = Path(pdf_basename).stem

    prefix = settings.CONFIG["output_settings"].get("annotated_file_prefix", "Notes - ")
    suffix = settings.CONFIG["output_settings"].get("annotated_file_suffix", "")
    file_format = settings.CONFIG["output_settings"].get("annotated_file_format", ".md")
    notes_folder = Path(settings.CONFIG.get("notes_folder"))

    # Dynamic Placeholder Replacement
    now = datetime.datetime.now()
    replacements = {
        "{date}": now.strftime("%Y-%m-%d"),
        "{time}": now.strftime("%H-%M-%S"),
        "{pdf_name}": pdf_basename,
        "{pdf_stem}": pdf_stem
    }
    
    for placeholder, val in replacements.items():
        prefix = prefix.replace(placeholder, val)
        suffix = suffix.replace(placeholder, val)

    apath = notes_folder / f"{prefix}{pdf_stem}{suffix}{file_format}"
    aname = f"{prefix}{pdf_stem}{suffix}"

    return aname, apath


def get_datestr():
    """Generates a date string based on the configuration settings.

    Returns:
        str: The formatted date string.
    """

    date_format = settings.CONFIG["output_settings"].get(
        "date_string_format", "%Y-%m-%d"
    )

    current_date = datetime.datetime.now()

    return current_date.strftime(date_format)


def get_timestr():
    """Generates a time string based on the configuration settings.

    Returns:
        str: The formatted time string.
    """

    time_format = settings.CONFIG["output_settings"].get(
        "time_string_format", "%H:%M:%S"
    )

    current_time = datetime.datetime.now()

    return current_time.strftime(time_format)


def get_datetime_str():
    """Generates a date-time string based on the configuration settings.

    Returns:
        str: The formatted date-time string.
    """

    datetime_format = settings.CONFIG["output_settings"].get(
        "datetime_string_format", "%Y-%m-%d %H:%M:%S"
    )

    current_datetime = datetime.datetime.now()

    return current_datetime.strftime(datetime_format)
