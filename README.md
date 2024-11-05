# PyMangaDL

PyMangaDL is a Python-based command-line tool that allows users to search for manga titles and download chapters along with their images. It utilizes asynchronous requests to fetch data efficiently from the MangaPill website.

## Features

- Search for manga titles by name.
- View detailed information about selected manga, including:
  - Japanese and English titles
  - Summary
  - Type
  - Status
  - Year of release
  - Genres
  - Total chapters
- Download selected chapters and their images.
- User-friendly command-line interface with prompts.
- **Progress Bar**: Display a progress bar during downloads.
- **Download Options**: Choose to download chapters as PDF or JPEG.

## Requirements

- Python 3.7 or higher

- Required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/OTAKUWeBer/PyMangaDL.git
   cd PyMangaDL
   ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the script:

   ```bash
   python main.py
   ```

4. Follow the prompts to search for manga and download chapters.

## How to Contribute

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
