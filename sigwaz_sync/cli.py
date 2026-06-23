import os
import json
import argparse
from pathlib import Path
import git

from .core_logic.converter import convert_single, ConversionConfig

class SigmaWazuhSyncPlugin:
    def __init__(self, target_wazuh_dir, sigma_repo_url="https://github.com/SigmaHQ/sigma.git", products=None):
        self.sigma_repo_url = sigma_repo_url
        self.target_wazuh_dir = Path(target_wazuh_dir).resolve()
        
        self.state_file = self.target_wazuh_dir / ".sigwaz_state.json"
        self.sigma_clone_path = self.target_wazuh_dir / ".sigma_upstream_clone"
        
        self.config = ConversionConfig()
        self.cli_products = products # Products passed via command line
        
    def _get_state(self):
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_state(self, commit_hash, products):
        with open(self.state_file, 'w') as f:
            json.dump({
                "last_commit": commit_hash,
                "products": products
            }, f)

    def _convert_and_write(self, sigma_file_path):
        try:
            if not str(sigma_file_path).endswith(('.yml', '.yaml')):
                return
                
            with open(sigma_file_path, 'r', encoding='utf-8-sig') as f:
                yaml_str = f.read()
                
            result = convert_single(yaml_str, self.config)
            
            if result.errors:
                print(f"[-] Skipped {sigma_file_path.name} (Parse Error): {'; '.join(result.errors)}")
                return
                
            if not result.xml:
                # This safely ignores rules that don't match our product filter
                return
            
            rel_path = os.path.relpath(sigma_file_path, self.sigma_clone_path)
            target_xml_path = self.target_wazuh_dir / "rules" / rel_path
            target_xml_path = target_xml_path.with_suffix('.xml')
            
            target_xml_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_xml_path, 'w', encoding='utf-8') as f:
                f.write(result.xml)
            print(f"[+] Converted: {rel_path}")
            
        except Exception as e:
            print(f"[-] Error processing {sigma_file_path.name}: {e}")

    def _delete_wazuh_rule(self, sigma_file_path):
        rel_path = os.path.relpath(sigma_file_path, self.sigma_clone_path)
        target_xml_path = self.target_wazuh_dir / "rules" / rel_path
        target_xml_path = target_xml_path.with_suffix('.xml')
        
        if target_xml_path.exists():
            target_xml_path.unlink()
            print(f"[-] Deleted rule: {rel_path}")

    def run_sync(self):
        print("Starting SigWaz GitOps Sync Engine...")
        
        # Load memory (state)
        state = self._get_state()
        last_commit = state.get("last_commit")
        saved_products = state.get("products")
        
        # Determine which products to filter (Append Mode: Merges Memory + CLI)
        effective_products_set = set()
        if saved_products:
            effective_products_set.update([p.strip() for p in saved_products.split(",") if p.strip()])
        
        if self.cli_products:
            effective_products_set.update([p.strip() for p in self.cli_products.split(",") if p.strip()])
            
        effective_products = ",".join(sorted(list(effective_products_set))) if effective_products_set else None
        
        if effective_products:
            # Tell the SigWaz core engine to ONLY convert these products
            self.config.allowed_products = [p.strip() for p in effective_products.split(",")]
            print(f"[*] Active Filter: Only converting rules for -> {effective_products}")
        else:
            print("[*] Active Filter: NONE (Converting ALL products)")

        if not self.sigma_clone_path.exists():
            print(f"[*] First run: Cloning upstream repository from {self.sigma_repo_url}...")
            repo = git.Repo.clone_from(self.sigma_repo_url, self.sigma_clone_path, depth=1)
            is_first_run = True
        else:
            print("[*] Fetching latest changes...")
            repo = git.Repo(self.sigma_clone_path)
            repo.remotes.origin.pull()
            is_first_run = False

        latest_commit = repo.head.commit.hexsha

        if is_first_run or not last_commit:
            print("[*] Performing FULL conversion. Please wait...")
            for root, _, files in os.walk(self.sigma_clone_path):
                for file in files:
                    self._convert_and_write(Path(root) / file)
        else:
            if latest_commit == last_commit:
                print("[*] No new changes in repository. Up to date!")
                # Still save state in case they updated their product filter
                self._save_state(latest_commit, effective_products)
                return

            print(f"[*] Calculating DELTA changes since last sync...")
            diffs = repo.commit(last_commit).diff(repo.head.commit)
            
            for diff in diffs:
                if diff.change_type in ['A', 'M', 'R']: 
                    file_path = diff.b_path if diff.b_path else diff.a_path
                    self._convert_and_write(self.sigma_clone_path / file_path)
                elif diff.change_type == 'D':
                    self._delete_wazuh_rule(self.sigma_clone_path / diff.a_path)
                    
        self._save_state(latest_commit, effective_products)
        print("[*] Sync Engine completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="SigWaz GitOps Plugin - Sync Sigma to Wazuh")
    parser.add_argument(
        "--target-dir", 
        required=True, 
        help="The local path where Wazuh rules should be written"
    )
    parser.add_argument(
        "--repo-url", 
        default="https://github.com/SigmaHQ/sigma.git",
        help="The Git URL or local path of the Sigma repository"
    )
    parser.add_argument(
        "--products", 
        default=None,
        help="Comma-separated list of products to convert (e.g. 'windows,linux,azure'). State is remembered for future syncs."
    )
    
    args = parser.parse_args()
    plugin = SigmaWazuhSyncPlugin(
        target_wazuh_dir=args.target_dir, 
        sigma_repo_url=args.repo_url,
        products=args.products
    )
    plugin.run_sync()

if __name__ == "__main__":
    main()