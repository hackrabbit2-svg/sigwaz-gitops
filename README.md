SigWaz GitOps Automation Engine

A DevSecOps automation pipeline that continuously monitors the upstream SigmaHQ repository (or a custom Sigma repo), converts new or modified rules into Wazuh-compatible XML, and manages your Detection-as-Code pipeline.

 Features

Stateful Product Filtering (Append Mode): Only convert the rules you actually need (e.g., Windows and Azure) so you don't overload your Wazuh Manager. The engine remembers and appends to your filters for all future delta syncs!

Delta Syncing: Remembers the last commit it processed and only converts the files that were added, modified, or deleted since the last run.

Shallow Cloning: Optimized Git operations that prevent massive downloads and network timeouts.

Fully Portable: Installs as a native command-line tool (sigwaz-sync) on any system via Python.

 Quick Start Guide: SigWaz GitOps Engine

This tool allows you to automatically pull the latest detection rules from the official SigmaHQ repository and convert them into Wazuh-ready XML files right on your laptop.

It features an intelligent Append Memory—it remembers what you download and only pulls the "new" stuff on future runs!

🛠️ Prerequisites

Make sure you have the following installed on your laptop:

Python (Version 3.8 or higher)

Git

Step 1: Install the Tool

Open your Command Prompt or Terminal to install it directly from this repository:

pip install git+[https://github.com/hackrabbit2-svg/sigwaz-gitops.git](https://github.com/hackrabbit2-svg/sigwaz-gitops.git)

Step 2: Create a Target Folder

Create an empty folder on your computer where you want your Wazuh XML rules to be saved.
For example: C:\wazuh-rules

Step 3: Your First Sync (Filter by Product)

The official Sigma repository has thousands of rules. To avoid generating irrelevant alerts and overloading your Wazuh Manager, use the --products flag to only download rules for the systems you actually monitor.

Run this command (change the path and products to fit your needs):

sigwaz-sync --target-dir C:\wazuh-rules --products windows,linux

Step 4: Future Syncs 

Scenario A: Routine Updates 
If you want to check for brand new Windows and Linux rules, you don't even need to type the products again. Just run:

sigwaz-sync --target-dir C:\wazuh-rules


It will instantly calculate the Git Delta, find any rules SigmaHQ added this week, and only convert the new ones!

Scenario B: Adding a new Product
If your company suddenly starts using Azure, just tell the tool:

sigwaz-sync --target-dir C:\wazuh-rules --products azure

The tool will instantly convert the Azure rules. AND it will permanently merge this into its memory! From now on, your normal syncs will automatically grab Windows, Linux, AND Azure.
