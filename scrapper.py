import os
import time
import wget
import math
import shutil
import pandas
import requests
import argparse
import itertools
from tqdm import tqdm
from mpire import WorkerPool
from colorama import init, Fore
from mpire.utils import make_single_arguments

# Function to download metadata from the camicroscope server
def get_image_metadata(uuid):
	flag 			= 0
	metadata_url 	= f'https://camic-viewer-prod.isb-cgc.org/camicroscope/api/Data/osdMetadataRetrieverFromSlideBarcode.php?imageId={uuid}'
	try:
		response 	= requests.get(metadata_url, timeout = 200)
		api_res 	= response.json()
	except Exception:
		print(f"{Fore.RED}{uuid} - failed (retrying after 120s)".center(columns))
		time.sleep(120)
		flag = 1
	if(flag):
		for i in range(2,5,1):
				try:
					flag 		= i
					response 	= requests.get(metadata_url, timeout = 200)
					api_res 	= response.json()
					break
				except Exception:
					print(f"{Fore.RED}{uuid} - failed (retrying after 120s)".center(columns))
					time.sleep(120)
	if(flag<5):
		try:
			api_res = response.json()
			return { "id": uuid, "image_url": api_res[1], "height": api_res[2], "width": api_res[3] }
		except:
			print(f"{Fore.RED}{uuid} - response failed {response.content}".center(columns))
			return { "id": uuid, "image_url": None }

# Creating a list of all the images url based on the size of the image (17X Zoom)
def get_image_urls(metadata):
	if(metadata['image_url'] != None):
		url_list 		= []
		pixel_width 	= math.ceil(int(metadata['width'])/frame_size)
		pixel_height 	= math.ceil(int(metadata['height'])/frame_size)
		for j in range(pixel_width):
			url_list.append([
				{
					'folder': f"{os.getcwd()}/{metadata['id']}/17/",
					'url'	: f"{metadata['image_url']}17/{j}_{k}.jpeg",
				} 
				for k in range(pixel_height)
			])
		return url_list
	print(f"{Fore.RED}{metadata['id']} - not found".center(columns))
	return []

# Downloading images and saving it to the respective folders
def download_images(link_info):
	try:
		wget.download(link_info['url'], bar = None, out = link_info['folder'])
	except:
		pass

# Initial Setup
init(autoreset = True)
columns 	= shutil.get_terminal_size().columns
frame_size 	= 256
level 		= list(range(5,18,1))

# Parser for input arguments
parser 		= argparse.ArgumentParser()
parser.add_argument('--file', help='Enter the file with the image uuid (tsv file) with header as uuid')
args 		= parser.parse_args()
file_url 	= args.file

# Reading the input file and parsing it as Dataframe
uuid_list 	= pandas.read_csv(file_url, sep = '\t', encoding = "utf-8", low_memory = False)

# Downloading all the metadata for the slides and saving it in a list with 50 threads
print(f"{Fore.GREEN}Downloading all Metadata for the slides provided".center(columns))
with WorkerPool(n_jobs = 50) as pool:
	metadata = pool.map(get_image_metadata, uuid_list['uuid'].to_list(), progress_bar = True)

print(f"{Fore.GREEN}Generating the list of urls to hit".center(columns))
with WorkerPool(n_jobs = 100) as pool:
	all_url = pool.map(get_image_urls, make_single_arguments(metadata, generator = False), progress_bar = True)

url_list = list(itertools.chain(*list(itertools.chain(*all_url))))
print(url_list[0])

print(f"{Fore.GREEN}Downloading the list of urls".center(columns))
with WorkerPool(n_jobs = 250) as pool:
	images = pool.map(download_images, make_single_arguments(url_list, generator = False), progress_bar = True)
