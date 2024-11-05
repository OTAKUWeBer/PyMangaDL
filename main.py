from bs4 import BeautifulSoup
import os
import asyncio
import aiohttp
import questionary
import subprocess
from termcolor import colored
import nest_asyncio
from tqdm import tqdm
from reportlab.pdfgen import canvas

nest_asyncio.apply()

# Define headers for the requests
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://mangapill.com/',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'Priority': 'u=5, i',
}

url = "https://mangapill.com"

# Clears the screen
def clear_screen():
    """Clear the console screen."""
    if os.name == 'nt':  # For Windows
        subprocess.run(['cls'], shell=True)
    else:  # For Unix/Linux/Mac
        subprocess.run(['clear'])

clear_screen()


# Searching manga
async def search():
    """Search for an manga and display the results."""
    while True:
        results = {}

        try:
            manga_search = questionary.text("Enter manga name to search or 'q' to quit: ",
                                            style=questionary.Style([('answer', 'fg:green')])).ask()
            if manga_search.lower() == 'q':
                clear_screen()
                print(colored("Exiting manga search.", 'red'))
                return
        except KeyboardInterrupt:
            print(colored("\nSearch interrupted. Exiting.", 'red'))
            return

        search_url = f'{url}/search?q={manga_search}'
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers) as response:
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        manga_list = soup.find_all("div", {"class": "flex flex-col justify-end"})  # Adjusted to find the correct div

        for div in manga_list:
            title_tag = div.find("a", class_="mb-2")  # Find the title link
            if title_tag:
                title = title_tag.find("div").text.strip()  # Get the title text
                link = title_tag.get("href")  # Get the href attribute
                results[title] = f"{url}{link}"

        if not results:
            clear_screen()
            print(colored("No results found. Please try searching again.", 'red'))
            continue

        choices = list(results.keys())
        selected_choice = questionary.select(
            "Select manga to see details, or 'q' to quit:",
            choices=choices + ["--quit"],
            style=questionary.Style([
                ('selected', 'fg:yellow'),
                ('pointer', 'fg:yellow'),
                ('highlighted', 'fg:yellow'),
                ('selected', 'bg:yellow fg:black'),
            ])
        ).ask()

        if selected_choice == 'q' or selected_choice == "--quit":
            clear_screen()
            print(colored("Exiting manga search.", 'red'))
            return

        selected_title = selected_choice
        selected_link = results[selected_title]
        await manga_details(selected_link)

# Print details about the manga
async def manga_details(manga_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(manga_url, headers=headers) as response:
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        jp_name = soup.find('h1', {"class": "font-bold text-lg md:text-2xl"})
        eng_name = soup.find('div', {"class": "text-sm text-secondary"})
        summary = soup.find('p', {"class": "text-sm text-secondary"})
        type = soup.find('label', {"class":'text-secondary'}, string='Type').find_next('div')
        status = soup.find('label',{"class":'text-secondary'}, string='Status').find_next('div')
        year = soup.find('label', {"class":'text-secondary'}, string='Year').find_next('div')
        genres = [a.get_text() for a in soup.find('label', {"class":'text-secondary'}, string='Genres')
                  .find_all_next('a', {"class": "text-sm mr-1 text-brand"})]
        total_chapter = soup.find('div', {"class":'my-3 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6'}).find_next('a')

        print(f"\033[1mTitle: {jp_name.get_text() if jp_name else 'None'}\033[0m")
        print(f"\033[1mEnglish Title: {eng_name.get_text() if eng_name else 'None'}\033[0m \n")
        print(f"\033[1mSummary:\033[0m {summary.get_text() if summary else 'None'}")
        print(f"\033[1mType:\033[0m {type.get_text() if type else 'None'}")
        print(f"\033[1mStatus:\033[0m {status.get_text() if status else 'None'}")
        print(f"\033[1mYear:\033[0m {year.get_text() if year else 'None'}")
        print(f"\033[1mGenres:\033[0m {', '.join(genres) if genres else 'None'}")
        print(f"\033[1mTotal Chapters:\033[0m {total_chapter.get_text().split(" ")[-1] if total_chapter else 'None'}")

        # Ask user if they want to download chapters
        download_choice = questionary.confirm("Download chapters from this manga?").ask()
        if download_choice:
            await fetch_chapter_links(manga_url, jp_name.get_text() if jp_name else eng_name.get_text())
        else:
            clear_screen()
            print(colored("Download cancelled.", 'red'))

# Fetch the chapter links

async def fetch_chapter_links(manga_url, title):
    async with aiohttp.ClientSession() as session:
        async with session.get(manga_url, headers=headers) as response:
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        chapters_div = soup.find('div', id='chapters')
        chapters_dict = {}

        # Find all anchor tags within the chapters div
        for a in chapters_div.find_all('a'):
            chapter_number = a.text.strip().split(" ")[-1]
            chapter_link = a['href']
            full_link = f"{url}{chapter_link}"
            chapters_dict[chapter_number] = full_link

        # Ask user which chapters to download
        chapter_numbers = questionary.text("Enter the chapters you want to download (space-separated): ").ask()
        chapters_to_download = chapter_numbers.split()

        # Ask user if they want to download as PDF or JPEG
        download_format = questionary.select(
            "Do you want to download the chapters as PDF or JPEG?",
            choices=["PDF", "JPEG"],
            style=questionary.Style([
                ('selected', 'fg:yellow'),
                ('pointer', 'fg:yellow'),
                ('highlighted', 'fg:yellow'),
                ('selected', 'bg:yellow fg:black'),
            ])
        ).ask()

        for chapter in chapters_to_download:
            if chapter in chapters_dict:
                chapter_dir = os.path.join("downloaded_manga", title, "Chapter " + chapter)
                os.makedirs(chapter_dir, exist_ok=True)
                print(f"Downloading chapter {chapter}...")
                image_paths = await fetch_image_links(session, chapters_dict[chapter], chapter_dir)

                if download_format == "PDF":
                    pdf_path = os.path.join(chapter_dir, f'Chapter_{chapter}.pdf')
                    create_pdf(image_paths, pdf_path)
                else:
                    print(f"Images downloaded to {chapter_dir}.")
            else:
                print(colored(f"Chapter {chapter} not available. Skipping.", 'red'))

# Get the links of the image
async def fetch_image_links(session, chapter_url, chapter_dir):
    async with session.get(chapter_url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')

        pages = soup.find_all('img', class_='js-page')
        total_pages = len(pages)
        image_paths = []

        # Create a tqdm progress bar for the entire chapter
        with tqdm(total=total_pages, desc='Downloading Images', unit='image') as pbar:
            tasks = []
            for index, page in enumerate(pages):
                img_url = page['data-src']
                file_path = os.path.join(chapter_dir, f'page_{index + 1}.jpeg')
                image_paths.append(file_path)  # Store the image path for PDF creation
                tasks.append(download_image(session, img_url, file_path, pbar))

            await asyncio.gather(*tasks)

        return image_paths  # Return the list of image paths

async def download_image(session, img_url, file_path, pbar):
    async with session.get(img_url, headers=headers) as response:
        if response.status == 200:
            with open(file_path, 'wb') as file:
                file.write(await response.read())
            pbar.update(1)  # Update the progress bar for each image downloaded
        else:
            print(f"Failed to download image from {img_url}")

def create_pdf(image_paths, pdf_path):
    c = canvas.Canvas(pdf_path)
    for image_path in image_paths:
        c.drawImage(image_path, 0, 0, width=600, height=800)  # Adjust size as needed
        c.showPage()  # Create a new page for each image
    c.save()
    print(f"PDF created: {pdf_path}")

# Starting
async def main():
    """Initiate the manga search."""
    await search()

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())