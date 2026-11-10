import sys
from urllib import parse

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

from RequestGuard import RequestGuard
import re
from byuimage import Image
from image_processing import sepia, grayscale, flipped, mirror

# C tag implementation
#region
def link_counting_main(args):
    """
    Coordinates the link-crawling execution.
    Validates the target URL, executes the traversal,
    generates a histogram of link frequencies using MatPlotLib,
    and exports the raw bin data to a CSV.
    """
    try:
        guard = RequestGuard(args[2])
        obj = guard.make_get_request(args[2])
    except Exception as e:
        print(f'Invalid arguments; Invalid URL; {e}')
        return
    url = args[2]
    visited = counting(url)
    frequencies = []
    for item in visited:
        frequencies.append(visited[item])
    bin_counts, bin_nums, item = plt.hist(frequencies, 5)
    plt.savefig(args[3])
    plt.clf()
    print_bins(bin_nums, bin_counts, args[4])


def process_links(link, current):
    """
    Normalizes scraped URLs by resolving relative paths against the base domain
    and stripping anchor fragments to prevent duplicate state tracking.
    """
    if link[0] == '#':
        return current
    if not re.findall(r'^http.+', str(link)):
        link = parse.urljoin(current, link)
    if '#' in str(link):
        return re.findall(r'(^http.+)#.+', str(link))[0]
    return link


def counting(url):
    """
    Executes a recursive web traversal starting from a root URL.
    Parses DOM elements via BeautifulSoup to extract anchor tags,
    strictly adhering to network constraints via the RequestGuard.
    Returns a dictionary mapping URLs to their occurrence frequency.
    """
    to_visit = [url]
    visited = {url: 1}
    guard = RequestGuard(url)
    obj = guard.make_get_request(url)
    if obj:
        soup = BeautifulSoup(obj.text, features="html.parser")
        to_visit = to_visit + [process_links(line['href'], url) for line in soup.find_all('a')]
        for link in to_visit:
            if link in visited:
                visited[link] += 1
            else:
                visited[link] = 1
                obj = guard.make_get_request(link)
                if obj:
                    soup = BeautifulSoup(obj.text, features="html.parser")
                    to_visit.extend([process_links(line['href'], link) for line in soup.find_all('a')])
    return visited


def make_lst(my_dict):
    """
    Flattens the frequency dictionary into a 1D array to interface with MatPlotLib
    histogram plotting constraints.
    """
    lst = []
    for item in my_dict:
        for i in range(int(my_dict[item])):
            lst.append(item)
    return lst


def print_bins(bin_nums, bin_counts, filename):
    """
    Exports generated histogram bin thresholds and counts to a structured CSV format.
    """
    with open(filename, 'w') as file:
        for value, count in zip(bin_nums, bin_counts):
            file.write(f'{value},{count}\n')
#endregion


# P tag implementation
#region
def print_data(args, rows):
    """
    Iterates over scraped table elements and exports the parsed,
    floating-point numeric data to a target CSV file.
    """
    with open(args[4], 'w') as file:
        for row in rows:
            line = ''
            for item in row:
                line += f'{float(item)},'
            line = line.strip(", ")
            file.write(f'{line}\n')


def plotting(args):
    """
    Scrapes HTML tables with specific target IDs. 
    Parses internal DOM structures, extracts numeric data arrays,
    and renders multi-line trend graphs using MatPlotLib before
    saving the visualization locally.
    """
    url = args[2]
    try:
        guard = RequestGuard(url)
        obj = guard.make_get_request(url)
    except Exception as e:
        print(f'Invalid arguments; Invalid URL; {e}')
        return

    if obj:
        soup = BeautifulSoup(obj.text, features="html.parser")
        found = soup.find_all('table')
        for item in found:
            if item.get('id') == 'CS111-Project4b':
                rows = item.find_all('tr')
                columns = [[],[],[],[],[]]
                new_rows = []
                for row in rows:
                    lst = row.find_all('td')
                    index = 0
                    new_row = []
                    for num in lst:
                        new_num = str(num).strip("</td>")
                        columns[index].append(float(new_num))
                        index += 1
                        new_row.append(new_num)
                    new_rows.append(new_row)

                x_points = columns[0]
                colors = ['b', 'g', 'r', 'k']
                iterator = iter(colors)
                for col in columns[1:]:
                    if col:
                        color = next(iterator)
                        plt.plot(x_points, col, color)
                plt.savefig(args[3])
                plt.clf()
                print_data(args, new_rows)
#endregion


# I tag implementation
def images(args):
    """
    The Image Pipeline router. Scrapes image sources (`<img>`) from the target URL,
    downloads the binary payload, and passes the payload directly into the external
    `image_processing` module for filtering (sepia, grayscale, transformations)
    before saving locally.
    """
    url = args[2]
    try:
        guard = RequestGuard(url)
        obj = guard.make_get_request(url)
    except Exception as e:
        print(f'Invalid arguments; Invalid image; {e}')
        return

    if obj:
        soup = BeautifulSoup(obj.text, features="html.parser")
        found = soup.find_all('img')
        for line in found:
            name = line.get('src')
            link = parse.urljoin(url, name)
            response = guard.make_get_request(link)
            with open(name, 'wb') as out_file:
                out_file.write(response.content)

            flag = args[4]
            if flag == '-s': # sepia
                image = sepia(name)
            elif flag == '-g': # grayscale
                image = grayscale(name)
            elif flag == '-f': # vertical flip
                image = flipped(name)
            elif flag == '-m': # horizontal flip
                image = mirror(name)
            else:
                print('Invalid arguments: Invalid flag (-s, -g, -f, or -m)')
                return
            filename = f'{args[3]}{name}'
            image.save(filename)


def main(args):
    """
    CLI entry point. Validates argument lengths and flags,
    routing the execution context to the Link Crawler (`-c`),
    the Data Plotter (`-p`), or the Image Pipeline (`-i`).
    """
    if len(args) >= 5:
        tag = args[1]
        if tag == '-c':
            link_counting_main(args)
        elif tag == '-p':
            plotting(args)
        elif tag == '-i':
            flag = args[4]
            if flag == '-s' or flag == '-g' or flag == '-f' or flag == '-m':
                images(args)
            else:
                print('Invalid arguments: Invalid flag (-s, -g, -f, or -m)')
                return
        else:
            print('Invalid arguments: Invalid flag (-c, -p, or -i)')
            return
    else:
        print('Invalid arguments; Not enough parameters')
        return



if __name__ == "__main__":
    main(sys.argv)