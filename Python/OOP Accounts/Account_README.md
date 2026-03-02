# 🏦 Bank Management System

A Python-based console application for managing bank accounts, credit cards, vaults, and transactions. Built with OOP principles using CSV files as persistent storage.

---

## 📁 Project Structure

```
.
├── oop_account_cls2.py      # All class definitions (OOP layer)
├── main1_account.py         # File 1 — Account management system
├── main2_transaction.py     # File 2 — Transaction system
├── account_data.csv         # Account data (primary data store)
├── account_log.csv          # Log of all account modifications
└── transaction_log.csv      # Log of all financial transactions
```

---

## 🛠️ Libraries & Tools

| Task | Library / Tool | Benefit |
|---|---|---|
| **Loading Data** | `csv.DictReader` | Maps CSV columns directly to class attributes |
| **Updating Data** | `csv.DictWriter` | Rewrites the file after every change to keep it in-sync |
| **Displaying Data** | `tabulate` | Makes the CLI look like a real banking application |
| **Tracking History** | `csv` (append mode) | Creates a permanent audit trail of every dollar moved |

---

## 📦 Requirements

- Python 3.10+
- [`tabulate`](https://pypi.org/project/tabulate/) — for table display

Install the dependency:
```bash
pip install tabulate
```
or
```bash
sudo apt install python3-tabulate
```

---

## 🚀 How to Run

### File 1 — Account Management
```bash
python3 main1_account.py
```
When prompted, enter:
- Account data CSV (e.g. `account_data.csv`)
- Account log CSV (e.g. `account_log.csv`)

### File 2 — Transaction System
```bash
python3 main2_transaction.py
```
When prompted, enter:
- Account data CSV (e.g. `account_data.csv`)
- Transaction log CSV (e.g. `transaction_log.csv`)

> Both programs load the **same** `account_data.csv`. Changes made in File 1 are immediately reflected when File 2 is run, and vice versa.

---

## 📄 CSV File Formats

### `account_data.csv`
| Column | Type | Description |
|---|---|---|
| `acc_num` | int | Unique account number |
| `acc_password` | str | Account password |
| `acc_balance` | float | Current account balance |
| `acc_type` | str | `credit_card` or `non_credit_card` |
| `credit_card_num` | str | Credit card number (`n/a` if not applicable) |
| `credit_card_pin` | str | Credit card PIN (`n/a` if not applicable) |
| `credit_card_limit` | float | Credit card limit (`n/a` if not applicable) |
| `vault` | str | `yes` or `no` |
| `vault_num` | str | Vault identifier (`n/a` if no vault) |
| `vault_password` | str | Vault lock password (`n/a` if no vault) |
| `vault_balance` | float | Current vault balance |

### `account_log.csv`
| Column | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM` |
| `acc_num` | Account number affected |
| `action` | e.g. `ACCOUNT_ADDED`, `VAULT_CREATED`, `CONVERT_TYPE`, `VAULT_DESTROYED` |
| `details` | Human-readable description of the change |

### `transaction_log.csv`
| Column | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM` |
| `acc_num` | Account number involved |
| `type` | `add`, `deduct`, `transfer_out`, `transfer_in`, `vault_add`, `vault_deduct`, `cc_payback_balance`, `cc_payback_cash` |
| `amount` | Transaction amount |
| `status` | `success`, `failed`, or `partial` |
| `balance_after` | Account balance after the transaction |

---

## 🏗️ Class Architecture (`oop_account_cls.py`)

### `Lock`
Holds a vault's lock password. Attached to every `Vault` instance.

| Attribute | Description |
|---|---|
| `lock_password` | The password string for this lock |

---

### `Vault`
Represents a secure vault attached to an account. **Not** an account itself — a separate object linked via `account.vault`.

| Attribute / Method | Description |
|---|---|
| `_vault_no` | Unique vault identifier (string, e.g. `V001`) |
| `_balance` | Current vault balance |
| `lock` | `Lock` instance holding the vault password |
| `add_funds(amount)` | Adds money to vault |
| `deduct_funds(amount)` | Deducts money; returns `False` if insufficient |

---

### `Account` (base class)
Shared foundation for all account types.

| Attribute / Method | Description |
|---|---|
| `_acc_num` | Unique account number (int) |
| `_acc_password` | Account password (str) |
| `_acc_balance` | Current balance (float) |
| `vault` | Attached `Vault` object, or `None` |
| `add_funds(amount)` | Adds to balance |
| `deduct_funds(amount)` | Deducts from balance; returns `False` if insufficient |
| `check_password(pwd)` | Returns `True` if password matches |
| `__iadd__(amount)` | `account += amount` syntax |
| `__isub__(amount)` | `account -= amount` syntax |

---

### `Non_Credit_Card(Account)`
Standard bank account with no credit card.

| Property | Description |
|---|---|
| `non_credit_card_info` | Dict with `acc_num`, `acc_type`, `acc_balance`, `vault` details |

---

### `CreditCard(Account)`
Account with an attached credit card. Inherits all `Account` behaviour plus:

| Attribute / Method | Description |
|---|---|
| `_credit_card_num` | Credit card number |
| `_credit_card_pin` | 1–4 digit PIN |
| `_credit_card_limit` | Maximum credit allowance |
| `_credit_used` | Running total of credit charged |
| `charge_credit(amount)` | Charges credit card; returns `False` if limit exceeded. Warns when ≤ $500 available |
| `payback_credit(amount)` | Reduces `_credit_used` |
| `check_cc_pin(pin)` | Returns `True` if PIN matches |
| `credit_card_info` | Dict with full account + credit card details |

---

### `Payment_Processor`
Handles all fund movement between accounts. Prints gateway-style output for every transaction.

| Method | Description |
|---|---|
| `add_funds(account, amount)` | Direct deposit to account balance |
| `deduct_funds(account, amount)` | Direct deduction from account balance. Warns if balance ≤ $500 after |
| `deduct_via_credit(cc, amount)` | Charges amount to credit card |
| `transfer_1to1(sender, receiver, amount, via_credit)` | Single transfer between two accounts |
| `transfer_1tomany(sender, receivers, amount, via_credit)` | One sender → list of receivers (same amount each) |
| `transfer_manyto1(senders, receiver, amount, via_credit)` | List of senders → one receiver (each sends the same amount) |

---

## 📋 Main File 1 — Account Management (`main1_account.py`)

### Main Menu
```
1. Modify Account
2. Show List
3. Show a particular account info
4. Show Account Log
5. Exit
```

### 1. Modify Account (Sub-menu)
| Option | Description |
|---|---|
| Add account | Creates a new account (non-credit or credit). Optionally attaches a vault. Logs `ACCOUNT_ADDED`. |
| Delete account | Confirms and removes an account. Logs `ACCOUNT_DELETED`. |
| Convert Non-Credit → Credit | Adds a credit card to an existing account. Logs `CONVERT_TYPE`. |
| Convert Credit → Non-Credit | Removes credit card from an account. Logs `CONVERT_TYPE`. |
| Create vault | Attaches a new vault (unique vault number + password). Logs `VAULT_CREATED`. |
| Destroy vault | Destroys vault after confirming fund transfer destination. Logs `VAULT_DESTROYED`. |

**Vault Destruction Flow:**
- If vault has funds, the user is asked where to transfer them:
  - **Account balance** → requires account password
  - **Credit card payback** *(credit card accounts only)* → requires credit card PIN
- Vault is only destroyed after successful authentication.

### 2. Show List (Sub-menu)
Filters and displays accounts by: All / Credit Card / Non-Credit Card / Has Vault / No Vault.

### 3. Show Particular Account
Prompts for `acc_num` and displays full account info.

### 4. Show Account Log (Sub-menu)
| Option | Description |
|---|---|
| Full list | Displays every log entry |
| For a particular account | Filters log by `acc_num` |

---

## 💸 Main File 2 — Transaction System (`main2_transaction.py`)

### Main Menu
```
1. Transaction
2. Manage Vault Balance
3. Payback Credit Card
4. Exit
```

### 1. Transaction (Sub-menu)

| Option | Description |
|---|---|
| Add Balance | Adds money directly to an account's balance |
| Deduct Balance | Deducts money from an account's balance |
| Transfer [1 to 1] | Transfers a fixed amount from one account to another |
| Transfer [1 to many] | Transfers the same amount from one sender to multiple receivers |
| Transfer [many to 1] | Each sender in a list transfers the same amount to one receiver |

**Transfer Authentication Flow** (options 3, 4, 5):

For every sender, the program asks:
1. Transfer from **account balance** or **credit card**? *(credit card option only appears for CC accounts)*
2. Authenticate: enter **account password** (balance) or **credit card PIN** (credit)
3. Money is always received into the **receiver's account balance**

**Warnings:**
- Account balance ≤ $500 → low balance warning after transaction
- Credit available ≤ $500 → low credit warning after charge
- Transfer from balance blocked if balance would go below $0
- Transfer from credit blocked if charge would exceed credit limit

### 2. Manage Vault Balance (Sub-menu)

All vault operations require the **vault lock password** first.

| Option | Sub-option | Description |
|---|---|---|
| Add money to vault | From account balance | Deducts from balance, adds to vault |
| Add money to vault | From credit card | Charges credit card, adds to vault |
| Deduct money from vault | To account balance | Moves vault money to account balance |
| Deduct money from vault | To credit card (pay back) | Uses vault money to pay back credit |

> Vault money **cannot** be transferred directly to another account — it must pass through the account balance first.

### 3. Payback Credit Card (Sub-menu)

| Option | Description |
|---|---|
| Via account balance | Deducts from account balance, reduces `credit_used`. Requires CC PIN. |
| Via instant cash | Directly reduces `credit_used` (external cash payment). Requires CC PIN. |

---

## ✅ Input Validation

All inputs are validated throughout both programs:

| Situation | Behaviour |
|---|---|
| String entered where int/float expected | Reprompts with error message |
| Negative number for balance/amount | Reprompts with error message |
| Invalid menu choice (e.g. `"to"` instead of `"yes"/"no"`) | Reprompts with error message |
| Uppercase input for yes/no choices | Accepted (converted to lowercase) |
| Duplicate `acc_num` | Rejected with message |
| Duplicate `credit_card_num` | Rejected with message |
| Duplicate `vault_num` | Rejected with message |
| Wrong password / PIN | Transaction cancelled, nothing saved |

---

## 🔐 Security Notes

- Passwords and PINs are stored as plaintext in the CSV (no hashing — suitable for educational use)
- The `__str__` methods never expose passwords or PINs in output
- Vault destruction and fund transfers from balance/credit require authentication every time

---

## *** Note :

- The 3 xlsx files `account_data.xlsx`, `account_log.xlsx`, and `transaction_log.xlsx` are preserved.
This setup ensures a reliable "start-over" capability, allowing you to reset your environment and rerun your analysis from a clean state at any time.
