# Samuda Growth Hub

Animated sales dashboard for Samuda Spec-Chem Limited (Adhesive, Thinner, DOP).

* The **page** (`index.html`) is published with GitHub Pages.
* The **data** stays in your Google account. A Google Apps Script builds it from your Google Sheets and gives it only to people who sign in with a user name and password.

## Files

| File | Where it goes | What it is |
|---|---|---|
| `index.html` | GitHub | The dashboard page with the sign-in screen |
| `config.json` | GitHub | Holds the link of the sign-in service: the **Cloudflare Worker** link (Part 4). The Apps Script link does not go on GitHub |
| `.github/workflows/update-dashboard.yml` | GitHub | Publishes the page after every change |
| `Code.gs` | Google Apps Script | Builds the data and checks the sign-in |
| `worker.js` | Cloudflare Worker | Security gate in front of the Apps Script (Part 4) |

## Part 1 - Google Sheets

1. **Source Sheets** (one per Excel file). In a blank Google Sheet: **File → Import → Upload** → choose the file → **Replace spreadsheet**.
   * Dump → tabs `SALES_ORDER`, `PRIMARY_SALES_COLLECTION`, `DELIVERY_ORDER`
   * Product master → tab `SKU_MASTER`
   * Customer master → tabs `Adhesive`, `Corporate`, `Thinner`
   * Budget (one Sheet per year, e.g. `SKU_BUDGET_2026`, `SKU_BUDGET_2025`) → any tab with the headings `DATE`, `ERP_SKU_CODE`, `ERP_SKU_NAME`, `BUDGET_QTY`, `BUDGET_VALUE`, one row per month and product
   These Sheets can stay **private** (Share → Restricted). Do not rename the tabs or the headings in row 1.
2. **Admin Sheet.** Create one more blank Google Sheet and name it `Dashboard Admin`.
3. In the Admin Sheet: **Extensions → Apps Script**. Delete the sample code, paste everything from `Code.gs`, press **Save** (disk icon).
4. Go back to the Admin Sheet and reload the page. A new menu **Dashboard** appears. Choose **Dashboard → Set up (first time)**.
   Google asks for permission once: **Continue → choose your account → Advanced → Go to (project name) → Allow**. Then choose **Set up** again.
5. Tab **Sources**: paste the links of the source Sheets in column A (one per row): dump, product master, customer master, and each budget Sheet.
6. Tab **Users**: one row per person - `Username`, `Password`, `Name`, `Active` (Yes/No). Type each password in the Password column; it is encrypted when you leave the cell. The set-up message shows the first `admin` password once - write it down.
7. **Dashboard → Update data now**. After 1–3 minutes a message shows the row counts.
8. **Dashboard → Turn on auto-update (when data changes)**.

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
   (only for the first test. For daily use put the **Worker** link here, Part 4: that is what keeps the Apps Script link off GitHub.)
4. **Settings → Pages → Source: GitHub Actions**.
5. Delete the files that are no longer needed: `data.json`, `sheets.txt`, `build_data.py`, `update_data.bat` and any `.xlsx` (open the file → ⋯ → Delete file).
6. Open the dashboard link. The sign-in screen appears.

**Old data in the repository history.** Deleted files can still be found in a repository's history. If `data.json` or the Excel files were ever uploaded to a public repository, the clean way is to create a **new repository**, upload only the files from the table above, and delete the old repository (Settings → General → Delete this repository).

## Part 4 - Cloudflare Worker (extra protection)

The Worker sits between the dashboard and the Apps Script:

`dashboard page → Cloudflare Worker → Apps Script → Google Sheets`

What it adds:
* The Apps Script link is hidden, and the script answers **only** requests that come through the Worker (they carry a secret key).
* Only your dashboard address may use the service from a browser.
* **Wrong** sign-in and password tries are limited to 10 per 10 minutes per internet connection (correct sign-ins are not counted, so a whole office can sign in).
* Anything that is not a small, well-formed dashboard request is refused before it reaches Google.

### Set-up

1. Sign up or sign in at https://dash.cloudflare.com.
2. **Workers & Pages → Create → Worker** (start from "Hello World"). Name it, for example, `samuda-hub`. Press **Deploy**.
3. Press **Edit code**. Delete everything, paste the contents of `worker.js`, press **Deploy**.
4. Open the Worker → **Settings → Variables and Secrets → Add** (three entries), then **Deploy**:

   | Type | Variable name | Value |
   |---|---|---|
   | Secret | `SCRIPT_URL` | your Apps Script web-app link (ends with `/exec`) |
   | Secret | `SHARED_KEY` | a long random text, 40 or more letters and numbers (keep a copy for step 9) |
   | Text | `ALLOWED_ORIGIN` | your dashboard address without the folder, e.g. `https://rafikuddin.github.io` |

5. Sign-in limit (recommended): **Storage & Databases → KV → Create** a namespace called `hub-limits`. Then Worker → **Settings → Bindings → Add → KV Namespace**, variable name `LIMITS`, choose `hub-limits`, **Deploy**.
6. Replace `Code.gs` in Apps Script with the new one, save, and publish it again: **Deploy → Manage deployments → pencil → Version: New version → Deploy** (the link stays the same).
7. On GitHub open `config.json` and replace the link with the Worker link shown on the Worker's page:
   `{ "api": "https://samuda-hub.YOUR-NAME.workers.dev" }`
8. Wait a minute for GitHub Pages, open the dashboard and sign in. It now works through the Worker.
9. **Last step:** in the Admin Sheet (reload it first) choose **Dashboard → Set Cloudflare key** and paste the same `SHARED_KEY`. From now on the Apps Script answers only the Worker.
10. Open the dashboard again and sign in once more to check.

To go back: **Dashboard → Remove Cloudflare key** and put the Apps Script link in `config.json` again.

### Keeping the Apps Script link off GitHub (and why the key matters)

* With the Worker in place, `config.json` holds only the **Worker** link. The Apps Script link lives in the Worker as the secret `SCRIPT_URL` and nowhere on GitHub.
* The Worker link is public on purpose: the browser has to call it. What protects the data is the **key** (`SHARED_KEY`): after **Dashboard → Set Cloudflare key**, the Apps Script answers nothing without it, so an old Apps Script link (for example one still in the GitHub history) is useless.
* **Do the key step last** (step 9), after you have signed in once through the Worker. If you set the key before `config.json` points to the Worker, the dashboard cannot sign in until you do.
* To be extra safe you can also create a **new** deployment (**Deploy → New deployment**, new link), paste the new link into the Worker's `SCRIPT_URL`, and archive the old deployment (**Manage deployments**).
* The workflow only ever publishes `index.html` and `config.json`; it warns you if `data.json`, Excel or CSV files are in the repository.

### What the Worker does not do

* It does not replace good passwords. Anyone with a correct user name and password can still sign in.
* The page file (`index.html`) stays public on GitHub. It holds no data.
* Whoever can open the Admin Sheet or your Google account controls everything, so protect that account with 2-step verification.

## Updating the numbers

Turn it on once: Admin Sheet → **Dashboard → Turn on auto-update (when data changes)**.

After that, just change the data:
* add or edit rows in a source Sheet, or
* import a new dump: **File → Import → Upload** → new file → **Replace spreadsheet**.

The script checks the source Sheets every 5 minutes. When something changed and the Sheets have been quiet for a minute, it rebuilds the dashboard data by itself (usually within 5–10 minutes). An open dashboard picks up the new data by itself and shows "New data loaded".

* To update at once: on the dashboard press **Update data → Update & reload** (any signed-in user), or in the Admin Sheet **Dashboard → Update data now**. Both do the same thing and take 1–3 minutes.
* To see what happened: **Dashboard → Auto-update status** (last build time, or the error if a build failed, for example a missing tab).
* A failed build is not repeated until the data changes again.

## Budget vs actual

* The **Budget vs actual** page compares the sales budget with order, delivery and collection: achievement %, gap, monthly chart, segment and category tables, and the SKU groups furthest behind or ahead.
* The budget comes from the budget Sheets listed in **Sources**. Add a new year by importing its file into a new Google Sheet and adding the link.
* The same budget value is used for all three comparisons. Volume uses BUDGET_QTY × TON factor.
* The budget is always the **full target** of the period (full month for MTD, January to that month for YTD).
* **Remaining** = budget − actual. **Daily RR (required rate)** = remaining ÷ working days left to the end of the period.
* Working days come from the **Holidays** tab of the Admin Sheet: column A/B = holiday dates (government and bank holidays), column D = weekly days off (Friday, Saturday). Add next year's holidays when the list is announced. Run **Dashboard → Set up (first time)** once to create the tab; it does not touch the other tabs.
* The budget is per product. Year, Month, Period and Product Category filters apply; Business Unit, Region, Area, Base, Day and Distributor do not.

## Users and passwords

### Managing users from the dashboard (admins)

Click the round badge with your initials at the top right of the dashboard.

* Everyone sees their own name and access, **Change my password** and **Sign out**.
* An **admin** also sees the list of users and can: **+ Add new user** (user name, full name, password, BU / Region / Area, Admin yes/no), switch a user **Active / Inactive** (an inactive user is signed out at once and cannot sign in), and **Reset password**.
* A new or reset password is shown once on the screen so you can pass it on; it is stored encrypted. The user can change it after signing in.
* Who is an admin: `Yes` in the **Admin** column of the Users tab. The column is added by itself when the Admin Sheet is opened, with `Yes` for the user named `admin`.
* You cannot switch off your own account. To change a user's BU / Region / Area or name, or to delete a user, edit the Users tab.

### Who sees what (BU / Region / Area)

The **Users** tab has three more columns: `BU`, `Region`, `Area`. They are added by themselves when the Admin Sheet is opened. (An older heading `Zone` is renamed to `Area` automatically; the names under it stay.)

| BU | Region | Area | The user sees |
|---|---|---|---|
| (empty) | (empty) | (empty) | everything (admin, management) |
| Thinner | | | the whole Thinner business unit |
| Thinner | WEST DSM | | only the WEST DSM region of Thinner |
| Thinner | CENTRAL DSM | Dhaka ZM | only that area |

* Write the names as in the customer master: `BU`, `REGION_BASE`, and `ASM_BASE` for the area (the Area filter on the dashboard). Capital and small letters do not matter.
* Several names in one cell: separate them with commas, for example `DOP, Adhesive`.
* **Dashboard → Check user access** lists every user, what they see and how many customers match, and flags names that are not in the customer master.
* The data is cut down on the server before it is sent, so a limited user's browser never receives other units' numbers.
* A limited user does not see the Budget page, because the budget is one figure for the whole company.
* A change takes effect the next time the user's dashboard loads data (reload the page, or **Sign everyone out**).

* Add, change or remove people in the **Users** tab. Put `No` in **Active** to block someone.
* **Passwords are stored encrypted** (a salted SHA-256 hash). Nobody can read them in the Sheet, not even you.
* **To give someone a password or reset a forgotten one:** type the new password into that person's **Password** cell and press Enter. It is encrypted at once. Tell the person the password and ask them to change it.
* **Users change their own password** on the dashboard: side menu → **Password**. They need the current password; the new one needs at least 8 characters. Their other devices are signed out.
* If a typed password stays readable (for example after pasting many rows), use **Dashboard → Encrypt passwords now**.
* A sign-in lasts 7 days with "Keep me signed in", otherwise 12 hours.
* After 5 wrong passwords the user name is locked for 10 minutes.
* **Dashboard → Sign everyone out** closes all sessions at once.

## Filters

Year · Month · Period (YTD / MTD) · **Day** · Business Unit · Region · **Area** · **Base** · Distributor · Product Category.

* **Day** shows one day of the month, for example 15: with Month = September it is 15 September 2026 against 15 September 2025; with Month = Auto and YTD it is the 15th of every month in the period. Choose **All** to switch it off. It does not apply to Pending delivery or to the Budget page.
* **Base** is `BASE_NAME` of the customer master. It follows the Area you pick (Business Unit → Region → Area → Base → Distributor). After installing the new `Code.gs`, run **Dashboard → Update data now** once so the Base names are added to the data.

## Details behind the numbers

* **Pending delivery** lists open order lines with the real **sales order number** (`Order Number` of SALES_ORDER, e.g. `SO-SSCL-DF-2026-001540`) in the *Order ref* column. Run **Dashboard → Update data now** after installing the new `Code.gs` so the numbers are added to the data.
* **Budget vs actual**: every card, ring, table row, bar and month of the chart opens a details panel. Sales budget, Order and Delivery cards, the TON rings, the segment / category rows and the "furthest behind / ahead" bars show budget, order and delivery side by side (by product, SKU group, category, segment or month; the month view adds Collection). The Collection card lists collections by distributor and month. Click a month in the chart to see that month only. *Download CSV* saves what is on screen.

## Notes

* Import the `.xlsx` file; do not copy-paste rows. Pasting can turn product codes such as `08-002` into dates.
* A Google Sheet holds at most 10 million cells; the dump uses about 5.5 million now. When it gets close, delete unused columns before importing (Approved By, Created By, Creation Date, Zone and Base columns).
* If `config.json` is missing or has no link, the page stays locked and says so. It never reads a public data file.
* The page only accepts a service link on `workers.dev` or `script.google.com` (see the `Content-Security-Policy` line at the top of `index.html`). If you later give the Worker your own domain, add it to `connect-src` there.
* Growth is like-for-like: only months with data in both years are compared. There are no budget or target figures in the data, so there is no achievement %.
