SigWaz GitOps Automation Engine

A DevSecOps automation pipeline that continuously monitors the upstream SigmaHQ repository (or a custom Sigma repo), converts new or modified rules into Wazuh-compatible XML, and manages your Detection-as-Code pipeline.

🚀 Features

Stateful Product Filtering (Append Mode): Only convert the rules you actually need (e.g., Windows and Azure) so you don't overload your Wazuh Manager. The engine remembers and appends to your filters for all future delta syncs!

Delta Syncing: Remembers the last commit it processed and only converts the files that were added, modified, or deleted since the last run.

Shallow Cloning: Optimized Git operations that prevent massive downloads and network timeouts.

Fully Portable: Installs as a native command-line tool (sigwaz-sync) on any system via Python.

📦 Installation for Analysts

You can install this tool on your local machine using any of the three methods below. Python 3.8+ and Git are required.

Option 1: Quick Install via CLI (Recommended)

pip install git+[https://github.com/YourUsername/sigwaz-gitops.git](https://github.com/YourUsername/sigwaz-gitops.git)


Option 2: Manual Clone via CLI

git clone [https://github.com/YourUsername/sigwaz-gitops.git](https://github.com/YourUsername/sigwaz-gitops.git)
cd sigwaz-gitops
pip install .


💻 How to Use the Tool (CLI)

Once installed, the sigwaz-sync command will be available globally on your terminal.

1. Standard Sync (All Rules)
To pull the latest official Sigma rules and convert them into a local Wazuh rules folder:

sigwaz-sync --target-dir C:\path\to\your\wazuh\rules


2. Filtering by Product (APPEND MODE)
The official Sigma repository contains thousands of rules. To prevent Wazuh from crashing due to irrelevant rules, use the --products flag.

This engine uses Append Mode memory! If you sync linux today, and run the command with azure tomorrow, the engine will remember both and sync azure,linux moving forward on any subsequent syncs.

sigwaz-sync --target-dir C:\path\to\your\wazuh\rules --products linux,azure


3. Custom Sigma Repository Sync
If your team maintains an internal/custom Sigma repository, you can point the engine directly to it instead of the public one:

sigwaz-sync --target-dir C:\path\to\your\wazuh\rules --repo-url [https://github.com/YourOrg/custom-sigma-rules.git](https://github.com/YourOrg/custom-sigma-rules.git)


☁️ Production Usage (GitHub Actions CI/CD)

This tool is designed to run completely headless in a CI/CD pipeline.

By pushing this repository to GitHub with the included .github/workflows/sigwaz-sync.yml file, GitHub Actions will automatically wake up every night at midnight, run this engine, and commit the newly converted Wazuh XML rules directly to your main branch so your Wazuh Manager can easily fetch them.