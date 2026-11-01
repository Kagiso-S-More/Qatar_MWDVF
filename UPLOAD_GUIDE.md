# Upload from Windows (recommended)

1. Create a new **empty** GitHub repository, e.g. `qatar-mwdvf-data` (do not initialize with a README).
2. Download/extract this template ZIP. Copy the entire content of your existing `Data` folder into the template's `Data` folder, allowing original files to replace placeholders **only after checking each target**. Preserve the `ACCESS-CM2` scenario and variable subfolders.
3. Open Git Bash or PowerShell in the template root (the directory containing README.md and .gitattributes). Install Git and Git LFS first.
4. Run:

```bash
git init
git lfs install
git add .
git lfs ls-files
git commit -m "Initial research data and analysis archive"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/qatar-mwdvf-data.git
git push -u origin main
```

5. Replace `YOUR-USERNAME` with your GitHub account. Authenticate when prompted.
6. Confirm on GitHub that NetCDF files are tracked by LFS and that all expected files are present.

**Before `git add .`:** review files for credentials, confidential data, third-party redistribution restrictions and unusually large files. GitHub web upload is not a good option for hundreds of `.nc` files; use Git + Git LFS. Do not commit raw files larger than Git LFS allows on your plan. If a push exceeds quota, use a separate data archive (e.g. Zenodo) and link it from the README.
