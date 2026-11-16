# Samuda Growth Hub

Animated sales dashboard for Samuda Spec-Chem Limited (Adhesive, Thinner, DOP).

* The **page** (`index.html`) is published with GitHub Pages.
* The **data** stays in your Google account. A Google Apps Script builds it from your Google Sheets and gives it only to people who sign in with a user name and password.

## Files

| File | Where it goes | What it is |
|---|---|---|
| `index.html` | GitHub | The dashboard page with the sign-in screen |
| `config.json` | GitHub | Holds the link of your Apps Script web app |
| `.github/workflows/update-dashboard.yml` | GitHub | Publishes the page after every change |
| `Code.gs` | Google Apps Script | Builds the data and checks the sign-in |

## Part 1 - Google Sheets

1. **Source Sheets** (one per Excel file). In a blank Google Sheet: **File → Import → Upload** → choose the file → **Replace spreadsheet**.
   * Dump → tabs `SALES_ORDER`, `PRIMARY_SALES_COLLECTION`, `DELIVERY_ORDER`
   * Product master → tab `SKU_MASTER`
   * Customer master → tabs `Adhesive`, `Corporate`, `Thinner`
   These Sheets can stay **private** (Share → Restricted). Do not rename the tabs or the headings in row 1.
2. **Admin Sheet.** Create one more blank Google Sheet and name it `Dashboard Admin`.
3. In the Admin Sheet: **Extensions → Apps Script**. Delete the sample code, paste everything from `Code.gs`, press **Save** (disk icon).
4. Go back to the Admin Sheet and reload the page. A new menu **Dashboard** appears. Choose **Dashboard → Set up (first time)**.
   Google asks for permission once: **Continue → choose your account → Advanced → Go to (project name) → Allow**. Then choose **Set up** again.
5. Tab **Sources**: paste the links of the three source Sheets in column A (one per row).
6. Tab **Users**: one row per person - `Username`, `Password`, `Name`, `Active` (Yes/No). Change the sample `admin` password.
7. **Dashboard → Update data now**. After 1–3 minutes a message shows the row counts.

## Part 2 - Turn the script into a web app

1. In the Apps Script editor: **Deploy → New deployment**.
2. Gear icon → **Web app**.
3. **Execute as: Me**. **Who has access: Anyone**. Press **Deploy**.
4. Copy the **Web app URL** (it ends with `/exec`).

"Anyone" only means anyone can reach the sign-in check; the data is given only after a correct user name and password.

If you change `Code.gs` later: **Deploy → Manage deployments → pencil → Version: New version → Deploy** (the link stays the same).

## Part 3 - GitHub

1. Upload `index.html` and `config.json` (**Add file → Upload files → Commit changes**).
2. Replace `.github/workflows/update-dashboard.yml` with the new one (open it → pencil → paste → commit).
3. Open `config.json` → pencil → paste the Web app URL between the quotes → commit:
   `{ "api": "https://script.google.com/macros/s/XXXX/exec" }`
4. **Settings → Pages → Source: GitHub Actions**.
5. Delete the files that are no longer needed: `data.json`, `sheets.txt`, `build_data.py`, `update_data.bat` and any `.xlsx` (open the file → ⋯ → Delete file).
6. Open the dashboard link. The sign-in screen appears.

**Old data in the repository history.** Deleted files can still be found in a repository's history. If `data.json` or the Excel files were ever uploaded to a public repository, the clean way is to create a **new repository**, upload only the files from the table above, and delete the old repository (Settings → General → Delete this repository).

## Updating the numbers

1. Open the dump Google Sheet → **File → Import → Upload** → new dump file → **Replace spreadsheet**.
2. Admin Sheet → **Dashboard → Update data now**.
3. On the dashboard: **Update data → Reload data**.

To make step 2 automatic: **Dashboard → Turn on hourly auto-update** (it rebuilds only when a source Sheet has changed).

## Users

* Add, change or remove people in the **Users** tab. Put `No` in **Active** to block someone.
* A sign-in lasts 7 days with "Keep me signed in", otherwise 12 hours.
* After 5 wrong passwords the user name is locked for 10 minutes.
* **Dashboard → Sign everyone out** closes all sessions at once.
* Passwords are stored as plain text in the Users tab, so share the Admin Sheet with nobody who should not see them, and do not reuse important passwords here.

## Notes

* Import the `.xlsx` file; do not copy-paste rows. Pasting can turn product codes such as `08-002` into dates.
* A Google Sheet holds at most 10 million cells; the dump uses about 5.5 million now. When it gets close, delete unused columns before importing (Approved By, Created By, Creation Date, Zone and Base columns).
* If `config.json` has no link, the page falls back to reading a public `data.json` without sign-in.
* Growth is like-for-like: only months with data in both years are compared. There are no budget or target figures in the data, so there is no achievement %.
