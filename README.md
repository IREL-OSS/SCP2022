# README

**This repository contains the scripts for the paper "A method for identifying references between projects in GitHub".**

## Scripts

We identify references between projects on the Github platform based on  **three steps**. Each step corresponds to a **script file**.


## Step1: Link extraction

**[Scripts/extract_links.py](https://github.com/IREL-OSS/SCP2022/blob/main/Scripts/extract_links.py)** contains the script to extract the links in descriptions and comments on issues, pull requests, and commits using patterns URL, Num, and SHA.

    #matching pattern: URL
    target1 = 'github.com/(.+?)/(.+?)'
    #matching pattern: Num
    target2 = '(.+?)/(.+?)#(\d+)'
    #matching pattern: SHA
    target3 = '(.+?)/(.+?)@([a-zA-Z0-9]+)'  

## Step2: Identify redirected projects

**[Scripts/identify_redirected_projects.py](https://github.com/IREL-OSS/SCP2022/blob/main/Scripts/identify_redirected_projects.py)** contains the script to identify the change of project names.

First, we build a project list based on the set of projects provided in the dataset. 
Then, we obtain the project’s current name by crawling the website information using the project’s original name. 
Next, we compare the project’s current name and original name to determine whether the project’s name changes. We replace the original project name with a new project name when the project’s name changes. 
Finally, we determine whether the reference’s source project and target project are the same. If they are the same, the reference is a within-project reference, and thus we filter out this reference.

## Step3: Filter references

**[Scripts/filter_references.py](https://github.com/IREL-OSS/SCP2022/blob/main/Scripts/filter_references.py)** contains the script to select references.

For a reference, we define the project where the reference appears in its issue, commit or pull request as the source project, and the project which the reference points to as the target project. 
We select references whose target projects belong to this project list. Otherwise, the references are filtered out because target projects do not belong to this project list. 
Next, we determine whether the reference’s source project and target project are the same. If they are the same, the reference is a within-project reference, and thus we filter out this reference. 
Finally, we obtain references between projects.
