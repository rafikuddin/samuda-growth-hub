# Samuda Growth Hub

Animated sales dashboard for Samuda Spec-Chem Limited (Adhesive, Thinner, DOP), published with GitHub Pages.

## Files in this repository

| File | What it is |
|---|---|
| `index.html` | The dashboard page: 8 views, with the filter bar (Year, Month, Business Unit, Region, Territory, Distributor, Product Category) at the top of every view |
| `data.json` | All the numbers. The page reads this file every time it opens |
| `build_data.py` | Makes `data.json` from the Excel workbook (keep it here or only on your computer) |
| `update_data.bat` | Double-click on Windows to run `build_data.py` |

Do **not** upload the Excel workbook.

## A. First-time GitHub setup

1. Go to https://github.com and sign up (or sign in).
2. Click **+** (top right) → **New repository**.
   * Repository name: `samuda-growth-hub`
   * Choose **Public**. GitHub Pages on a free account works only for public repositories. (A private repository needs a paid plan such as GitHub Pro, and the published page is still open to anyone who has the link.)
   * Tick **Add a README file** → **Create repository**.
3. In the repository click **Add file → Upload files**. Drag in `index.html`, `data.json`, `build_data.py`, `update_data.bat`, `README.md` → **Commit changes**.

## B. Turn on GitHub Pages

1. In the repository open **Settings** (top menu) → **Pages** (left menu).
2. Under **Build and deployment → Source** choose **Deploy from a branch**.
3. Under **Branch** choose **main** and **/ (root)** → **Save**.
4. Wait 1–2 minutes and refresh the page. The link appears at the top:
   `https://<your-username>.github.io/samuda-growth-hub/`
5. Open the link. Bottom-left of the dashboard should say **GitHub data.json** with the build date.

## C. One-time setup on your computer (for updating the data)

1. Install Python 3 from https://www.python.org/downloads/ and tick **Add python.exe to PATH** in the installer.
2. Open **Command Prompt** and run: `pip install pandas openpyxl`
3. Put `build_data.py`, `update_data.bat` and `Samuda_Growth_Dashboard_v5.xlsx` in the same folder.

## D. Updating the numbers (every time)

1. Paste the new dump into the workbook (or Data → Refresh All) and **save** it.
2. Double-click `update_data.bat`. After about 30 seconds a new `data.json` appears in the folder.
3. On GitHub: **Add file → Upload files** → drop `data.json` → **Commit changes** (it replaces the old one).
4. After a minute open the dashboard and press **Update data → Reload from GitHub** (or Ctrl+F5).

## Notes

* If the workbook file name changes, edit the name inside `update_data.bat`.
* The page must be opened from the GitHub Pages link. Opened as a file from your computer it cannot read `data.json`.
* Order, Delivery and Collection use the workbook's rules (Total Amount / Delivery Amount / Collection Amount, top 80%, rubber adhesive keyword). With no filter they match the Excel dashboard.
* Growth is like-for-like: only months with data in both years are compared. Delivery growth shows n/a until 2025 delivery rows are added.
* Product Category does not apply to collection (collection is booked per customer). Year and Month do not change Pending delivery (it is a snapshot of open orders).
* The workbook has no budget or target figures, so there is no achievement %.
* `data.json` contains distributor names and monthly sales totals per distributor and product. Anyone who has the page link can read it, whether the repository is public or private. Share the link only with people who may see these numbers.
