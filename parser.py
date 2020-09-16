import os
import requests
import json
import csv
from bs4 import BeautifulSoup

domain = "https://github.com"
repo_link = "https://github.com/Bukkit/Bukkit" # change url
repo_name = repo_link.split('/')[-1]
os.mkdir(repo_name)


def get_commits_from_page(soup):
    raw_links = soup.findAll("p", {"class": "mb-1"})
    return [link.a.attrs.get("href") for link in raw_links]


def find_commit_links(next_page, max_commits=50):
    links = []
    while len(links) < max_commits and next_page is not None:
        page = requests.get(next_page)
        soup = BeautifulSoup(page.content, 'html.parser')
        links += get_commits_from_page(soup)
        bottom = soup.find("div", {"class": "paginate-container"}).find("a")
        next_page = bottom.attrs.get("href") if bottom.text == "Older" else None
    return links[:50]


def help_find_text(class_name, file):
    rows = file.findAll("td", {"class": class_name})
    result = []
    if not rows:
        return result

    for row in rows:
        result.append(row.find("span", {"class": "blob-code-inner blob-code-marker"}).text)
    return result


def build_commit_data(folder, commit_ind, url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    author = soup.find(attrs={"class": "commit-author user-mention"}).text

    files_container = soup.find("div", {"id": "files"})
    files = files_container.findAll("div", {"data-details-container-group": "file"})

    commit_data = []
    data_for_csv = []
    for file in files:
        file_path = file.find("div", {"class": "file-info flex-auto min-width-0 mb-md-0 mb-2"}).find("a").text
        name_parts = file_path.split('/')[-2:]
        name = "/".join(name_parts)
        deleted = file.find("div", {"data-file-deleted": "true"}) is not None

        new_rows = help_find_text("blob-code blob-code-addition", file)
        removed_rows = help_find_text("blob-code blob-code-deletion", file)

        data_for_csv.append([len(new_rows) + len(removed_rows), name])

        file_dict = {"name": name,
                     "is_deleted": deleted,
                     "new_rows": new_rows,
                     "removed_rows": removed_rows}
        commit_data.append(file_dict)

    commit_dict = {"files": commit_data}
    result_json = json.dumps(commit_dict)

    with open('{0}/{1}.json'.format(folder, commit_ind), 'w') as f:
        f.write(result_json)

    with open('{0}/commit_data.csv'.format(folder), 'a', encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        for row in data_for_csv:
            writer.writerow([commit_ind, author] + row)


commit_links = find_commit_links(repo_link + "/commits/master")

with open('{0}/commit_data.csv'.format(repo_name), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["ind", "author", "changed_rows", "file_name"])

for ind, link in zip(range(1, len(commit_links) + 1), commit_links):
    build_commit_data(repo_name, ind, domain + link)
