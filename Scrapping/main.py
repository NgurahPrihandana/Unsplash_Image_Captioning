import requests
import os
import time


class UnsplashImageDownloader:
    def __init__(self, query):
        self.querystring = {"query": f"{query}", "per_page": "20"}
        self.headers = {"cookie": "ugid=aacdcdf3a2acebee349c2e196e621b975571725"}
        self.url = "https://unsplash.com/napi/search/photos"
        self.query = query

    def get_total_images(self):
        with requests.request("GET", self.url, headers=self.headers, params=self.querystring) as rs:
            json_data = rs.json()
        return json_data["total"]

    def get_links(self, pages_, quality_):
        all_links = []
        for page in range(1, int(pages_) + 1):
            self.querystring["page"] = f"{page}"

            response = requests.request("GET", self.url, headers=self.headers, params=self.querystring)
            response_json = response.json()
            all_data = response_json["results"]

            for data in all_data:
                # Get the title/alt description for each image
                name = data.get('alt_description') or data.get('description') or "untitled"
                # Remove any unsafe characters for filenames
                safe_name = "".join(c for c in name if c.isalnum() or c in " _-").rstrip()

                try:
                    # Get image URL of specified quality
                    image_url = data["urls"][quality_]
                    all_links.append((image_url, safe_name))
                    print(f"name: {safe_name}\nurl: {image_url}\n")
                except KeyError:
                    pass  # Skip if the quality is not found

        return all_links


def download_images(image_links, folder):
    for index, (url, name) in enumerate(image_links):
        filename = os.path.join(folder, f"{name}_{index}.jpg")
        try:
            img_data = requests.get(url).content
            with open(filename, 'wb') as handler:
                handler.write(img_data)
            print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


if __name__ == '__main__':
    folder = "unsplash"
    if not os.path.exists(folder):
        os.mkdir(folder)

    search = input("What you want to search for? ")

    unsplash = UnsplashImageDownloader(search)

    total_image = unsplash.get_total_images()
    print("\ntotal images available: ", total_image)

    if total_image == 0:
        print("sorry, no image available for this search")
        exit()

    number_of_images = int(input("Enter number of images you want to download: "))

    if number_of_images == 0 or number_of_images > total_image:
        print("Not a valid number")
        exit()

    pages = int(number_of_images / 20) + (1 if number_of_images % 20 != 0 else 0)

    print("\nAvailable image quality: raw, full, regular, small, thumb, small_s3\n")

    quality = input("Enter the quality: ")
    image_links = unsplash.get_links(pages, quality)

    start = time.time()
    print("Download started...\n")

    # Download images
    download_images(image_links, folder)

    print("\nDownloading finished.")
    print("Time taken: ", time.time() - start)
