# Samuda Growth Hub

Animated sales dashboard for Samuda Spec-Chem Limited (Adhesive, Thinner, DOP), published with GitHub Pages.

## Files in this repository

| File | What it is |
|---|---|
| `index.html` | The dashboard page: 8 views, with the filter bar (Year, Month, Business Unit, Region, Territory, Distributor, Product Category) at the top of every view |
| `data.json` | All the numbers. The page reads this file every time it opens |
| `build_data.py` | Makes `data.json` from the Excel files (dump, product master, customer master) |
| `update_data.bat` | Double-click on Windows to run `build_data.py` |
| `.github/workflows/update-dashboard.yml` | The automatic update: rebuilds `data.json` and republishes after every upload |

The Excel files are needed in the repository only for the automatic update (section C).

## A. First-time GitHub setup

1. Go to https://github.com and sign up (or sign in).
2. Click **+** (top right) → **New repository**.
   * Repository name: `samuda-growth-hub`
   * Choose **Public**. GitHub Pages on a free account works only for public repositories. (A private repository needs a paid plan such as GitHub Pro, and the published page is still open to anyone who has the link.)
   * Tick **Add a README file** → **Create repository**.
3. In the repository click **Add file → Upload files**. Drag in `index.html`, `data.json`, `build_data.py`, `update_data.bat`, `README.md` → **Commit changes**.

## B. Turn on GitHub Pages

1. Add the workflow file: **Add file → Create new file**, type the name `.github/workflows/update-dashboard.yml`, paste the contents of `update-dashboard.yml`, **Commit changes**.
2. Open **Settings** (top menu) → **Pages** (left menu).
3. Under **Build and deployment → Source** choose **GitHub Actions**.
4. Open the **Actions** tab → **Update dashboard** → **Run workflow**. After the green tick the link is shown in the run and in Settings → Pages:
   `https://<your-username>.github.io/samuda-growth-hub/`
5. Open the link. Bottom-left of the dashboard should say **GitHub data.json** with the build date.

## C. Automatic update (GitHub does the work)

Needs `.github/workflows/update-dashboard.yml` in the repository and **Settings → Pages → Source = GitHub Actions**.

1. On GitHub: **Add file → Upload files**. Drop the three Excel files:
   * the dump (sheets `SALES_ORDER`, `PRIMARY_SALES_COLLECTION`, `DELIVERY_ORDER`)
   * the product master (sheet `SKU_MASTER`)
   * the customer master (sheets `Adhesive`, `Corporate`, `Thinner`)
2. Press **Commit changes**.
3. GitHub builds a new `data.json` and republishes the dashboard in about 2–3 minutes. Watch it in the **Actions** tab (green tick = done).

Rules:
* Keep the **same file names** every time, so the new upload replaces the old file. The script finds the data by sheet name, so the file name itself can be anything, but two dump files with different names in the repository would confuse it.
* You can upload only the file that changed (for example only the dump).
* GitHub's website refuses files over 25 MB. The dump is already about 24 MB; when it grows past the limit, use section D instead (or GitHub Desktop).
* In a public repository the uploaded Excel files can be downloaded by anyone, with every order line, price and customer.

## D. Manual update (data stays on your computer)

One-time: install Python 3 from https://www.python.org/downloads/ (tick **Add python.exe to PATH**), then run `pip install pandas openpyxl` in Command Prompt.

1. Put the three Excel files in the same folder as `build_data.py` and `update_data.bat`.
2. Double-click `update_data.bat`. After about 40 seconds a new `data.json` appears.
3. On GitHub: **Add file → Upload files** → drop `data.json` → **Commit changes**.

## Notes

* The page must be opened from the GitHub Pages link. Opened as a file from your computer it cannot read `data.json`.
* Order, Delivery and Collection use the workbook's rules (Total Amount / Delivery Amount / Collection Amount, top 80%, rubber adhesive keyword). With no filter they match the Excel dashboard.
* Growth is like-for-like: only months with data in both years are compared. Delivery growth shows n/a until 2025 delivery rows are added.
* Product Category does not apply to collection (collection is booked per customer). Year and Month do not change Pending delivery (it is a snapshot of open orders).
* The workbook has no budget or target figures, so there is no achievement %.
* `data.json` contains distributor names and monthly sales totals per distributor and product. Anyone who has the page link can read it, whether the repository is public or private. Share the link only with people who may see these numbers.
