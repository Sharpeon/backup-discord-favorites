import json
import requests
import time
import threading
import os
import sys
from multiprocessing.pool import ThreadPool


FAVORITES_DIR = "./favorites/"
DATA_FILE = "data.json"
URLS_OUTPUT_FILE = "output.txt"

current_download = 0

def get_data_dict():
    """Returns the data of favorites as a dictionnary"""
    if os.path.getsize(DATA_FILE) == 0:
        raise Exception("The data json file is empty. Did you follow the steps correctly ?")

    with open(DATA_FILE) as f:
        data = json.load(f)

    return data

def get_gifs_urls(favorites):
    """Returns the urls of the gifs of the favorites
    Some favorites also have a mp4 link some reason, I only pick the gifs."""

    urls = []
    for favorite in favorites:
        url = favorite["url"]
        src = favorite["src"]
        
        # We dont want mp4 >:(
        if src.endswith("mp4"):
            urls.append(url)
        else:
            urls.append(src)

    return urls

def write_urls_to_file(urls):
    """Writes the gifs urls to a file"""
    with open(URLS_OUTPUT_FILE, "w") as f:
        for url in urls:
            f.write(url + "\n")

def download_gif(url):
    """Download the gif"""
    file_name_start_pos = url.rfind("/") + 1
    file_name = url[file_name_start_pos:]
    global current_download

    # Add ".gif" extension if it doesnt exist
    if not file_name.endswith(".gif"):
        file_name += ".gif"
    
    r = requests.get(url, stream=True)
    if r.status_code == requests.codes.ok:
        with open(FAVORITES_DIR + file_name, "wb") as f:
            for data in r:
                f.write(data)
    else:
        print("Error downloading " + url)
        
    current_download += 1
    return url

def show_advancement(total):
    """Shows the advancement of the download in percentage"""
    global current_download

    while current_download < total:
        advancement = int(current_download / total * 100)
        print("Downloading... " + str(advancement) + "%", end="\r")
        time.sleep(1)
        

def main():
    data = get_data_dict()
    favorites = data["_state"]["favorites"]
    gifs_urls = get_gifs_urls(favorites)

    # Save the urls to a file
    write_urls_to_file(gifs_urls)
    print("Your favorite gifs urls have been saved to " + URLS_OUTPUT_FILE + "\n") 

    # Asking if they want to download all the gifs
    while True:
        answer = input("Do you want to download all the gifs?\nIt might take a while if you have a lot (y/n) ")
        if answer == "y":
            advancement_thread = threading.Thread(target=show_advancement, args=(len(gifs_urls),))
            advancement_thread.start()
            
            # Creates directory if it doesnt exist
            if not os.path.exists(FAVORITES_DIR):
                os.makedirs(FAVORITES_DIR)

            # Downloading all the gifs
            pool = ThreadPool(10)
            pool.map(download_gif, gifs_urls)
            pool.close()
            pool.join()
            
            output_dir = os.path.dirname(sys.argv[0]) + FAVORITES_DIR[1:-1]
            print("\nDone downloading! Ouput directory is : " + output_dir)

            break
        elif answer == "n":
            break

    # Say goodbye
    print("Have a nice day ! :)")

if __name__ == "__main__":
    main()
