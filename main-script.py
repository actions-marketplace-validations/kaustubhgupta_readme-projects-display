from github import Github
import pathlib
import re
import sys
import json


def rewriteContents(old_content, new_content):
    r = re.compile(
        r'<!\-\- PROJECTS START \-\->.*<!\-\- PROJECTS END \-\->', re.DOTALL)
    new_content_formated = '<!-- PROJECTS START -->{}<!-- PROJECTS END -->'.format(
        new_content)
    return r.sub(new_content_formated, old_content)

git = Github(sys.argv[1])
start = git.rate_limiting[0]
max_repo_description = int(sys.argv[4])
allow_forks = bool(sys.argv[5])
project_sort_by = sys.argv[6]
print(f'Request left at start of the script: {start}')

user_object = git.get_user()
git_username = user_object.login

repo_list = [repo.name for repo in user_object.get_repos()]
project_data = {}

print("=====================REPO CHECK BEGINS=============================")
for repo in repo_list:
    print(f'Repo being checked: {repo}')
    try:
        repo_object = git.get_repo(git_username + '/' + repo)
        repo_topics = repo_object.get_topics()
        if len(repo_topics) != 0:
            if 'project' in repo_topics:
                project_data[f'{repo}'] = {'repo_description': repo_object.description if len(repo_object.description) < max_repo_description else repo_object.description[:max_repo_description] + '...',
                                           'repo_stars': int(repo_object.stargazers_count),
                                           'repo_link': f'https://github.com/{git_username}/{repo}',
                                           'repo_forks': int(repo_object.forks_count)
                                           }

            else:
                continue
        else:
            continue
    except:
        continue


end = git.rate_limiting[0]
print(f'Request left at end of the script: {end}')
print(f'Requests Consumed in this process: {start - end}')
print("=====================REPO CHECK ENDS=============================")

sort_key = 'repo_' + project_sort_by
project_data_sorted = dict(
    sorted(project_data.items(), key=lambda x: x[1][sort_key])[::-1])


repoName = sys.argv[3].split('/')[-1]
readme_path = sys.argv[3] + f'/{sys.argv[2]}'
with open(readme_path, 'r', encoding='utf-8') as f:
    readme = f.read()

readmeRepo = git.get_repo(f"{git_username}/{repoName}")
contents = readmeRepo.get_contents(f'{sys.argv[2]}')

newContent = []
if allow_forks:
    for project, project_detail in project_data_sorted.items():
        newContent.append(
            f'\n* [{project}]({project_detail["repo_link"]}) **{project_detail["repo_stars"]}⭐, {project_detail["repo_forks"]}** forks ({project_detail["repo_description"]})')
else:
    for project, project_detail in project_data_sorted.items():
        newContent.append(
            f'\n* [{project}]({project_detail["repo_link"]}) **{project_detail["repo_stars"]}⭐** ({project_detail["repo_description"]})')

newContent = ' '.join(newContent)
rewrittenReadme = rewriteContents(readme, newContent)
print("=====================RESULTS=============================")
if rewrittenReadme != readme:
    print("Repo Contents Updated")
    readmeRepo.update_file(contents.path, "Updating Projects Section",
                        rewrittenReadme, contents.sha)
else:
    print("No change detected in file contents")
