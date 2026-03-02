"""
main1_account.py
Account Management System — Main File 1
Handles: account CRUD, type conversion, vault management, account log.
Usage: python main1_account.py
"""

import csv
import os
import datetime
from tabulate import tabulate
from oop_account_cls import Account, Non_Credit_Card, CreditCard, Vault, Payment_Processor

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

FIELDNAMES = [
    "acc_num", "acc_password", "acc_balance", "acc_type",
    "credit_card_num", "credit_card_pin", "credit_card_limit",
    "vault", "vault_num", "vault_password", "vault_balance"
]

LOG_FIELDNAMES = ["timestamp", "acc_num", "action", "details"]


# ─────────────────────────────────────────────────────────────────────────────
#  CSV helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_accounts(filename: str) -> dict:
    """Read CSV → {acc_num (int): Account object}. Uses csv.DictReader to map
    columns directly to class attributes."""
    accounts = {}
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            acc_num      = int(row["acc_num"])
            acc_password = row["acc_password"].strip()
            acc_balance  = float(row["acc_balance"])
            acc_type     = row["acc_type"].strip().lower()
            cc_num       = row["credit_card_num"].strip()
            cc_pin       = row["credit_card_pin"].strip()
            cc_limit     = row["credit_card_limit"].strip()
            has_vault    = row["vault"].strip().lower() == "yes"
            vault_num    = row["vault_num"].strip()
            vault_pwd    = row["vault_password"].strip()
            vault_bal_raw = row.get("vault_balance", "").strip()
            vault_bal    = float(vault_bal_raw) if vault_bal_raw not in ("", "n/a") else 0.0

            if acc_type == "credit_card":
                obj = CreditCard(acc_num, acc_password, acc_balance,
                                 cc_num, cc_pin, float(cc_limit))
            else:
                obj = Non_Credit_Card(acc_num, acc_password, acc_balance)

            if has_vault and vault_num != "n/a":
                obj.vault = Vault(vault_num, vault_bal, vault_pwd)

            accounts[acc_num] = obj
    return accounts


def save_accounts(filename: str, accounts: dict):
    """Rewrite CSV with all current data (csv.DictWriter keeps file in-sync
    after every change)."""
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for obj in accounts.values():
            is_cc     = isinstance(obj, CreditCard)
            has_vault = obj.vault is not None
            writer.writerow({
                "acc_num":           obj._acc_num,
                "acc_password":      obj._acc_password,
                "acc_balance":       obj._acc_balance,
                "acc_type":          "credit_card" if is_cc else "non_credit_card",
                "credit_card_num":   obj._credit_card_num    if is_cc    else "n/a",
                "credit_card_pin":   obj._credit_card_pin    if is_cc    else "n/a",
                "credit_card_limit": obj._credit_card_limit  if is_cc    else "n/a",
                "vault":             "yes" if has_vault else "no",
                "vault_num":         obj.vault._vault_no           if has_vault else "n/a",
                "vault_password":    obj.vault.lock.lock_password   if has_vault else "n/a",
                "vault_balance":     obj.vault._balance             if has_vault else "n/a",
            })
    print("\n  [SYSTEM] CSV saved successfully.")


def append_log(log_file: str, acc_num: int, action: str, details: str):
    """Append one row to the account log CSV in append mode — permanent audit trail."""
    timestamp   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    file_exists = os.path.exists(log_file) and os.path.getsize(log_file) > 0
    if file_exists:
        with open(log_file, "rb") as f:
            f.seek(-1, 2)
            last_byte = f.read(1)
        if last_byte not in (b"\n", b"\r"):
            with open(log_file, "a") as f:
                f.write("\n")
    with open(log_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"timestamp": timestamp, "acc_num": acc_num,
                         "action": action, "details": details})


def load_log(log_file: str) -> list:
    """Return all log rows as a list of dicts."""
    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        return []
    with open(log_file, newline="") as f:
        rows = list(csv.DictReader(f))
    # Filter out rows that don't have all required fields (corrupted entries)
    return [r for r in rows if all(k in r and r[k] is not None for k in LOG_FIELDNAMES)]


# ─────────────────────────────────────────────────────────────────────────────
#  Uniqueness helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_all_cc_nums(accounts: dict) -> set:
    return {obj._credit_card_num for obj in accounts.values() if isinstance(obj, CreditCard)}

def get_all_vault_nos(accounts: dict) -> set:
    return {obj.vault._vault_no for obj in accounts.values() if obj.vault}


# ─────────────────────────────────────────────────────────────────────────────
#  Input-validation helpers
# ─────────────────────────────────────────────────────────────────────────────

def ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(prompt).strip().lower()
        if   ans == "yes": return True
        elif ans == "no":  return False
        else: print("  Invalid — please type 'yes' or 'no'.")

def ask_acc_type() -> str:
    while True:
        t = input("  Account type (credit_card / non_credit_card): ").strip().lower()
        if t in ("credit_card", "non_credit_card"): return t
        print("  Invalid — please type 'credit_card' or 'non_credit_card'.")

def ask_positive_int(prompt: str) -> int:
    while True:
        try:
            v = int(input(prompt))
            if v > 0: return v
            print("  Must be greater than zero.")
        except ValueError:
            print("  Invalid — enter a whole number.")

def ask_non_negative_float(prompt: str) -> float:
    while True:
        try:
            v = float(input(prompt))
            if v >= 0: return v
            print("  Cannot be negative.")
        except ValueError:
            print("  Invalid — enter a number.")

def ask_positive_float(prompt: str) -> float:
    while True:
        try:
            v = float(input(prompt))
            if v > 0: return v
            print("  Must be greater than zero.")
        except ValueError:
            print("  Invalid — enter a number.")

def ask_menu_choice(valid: list, prompt: str = "  Select option: ") -> str:
    while True:
        c = input(prompt).strip()
        if c in valid: return c
        print(f"  Invalid — choose from: {', '.join(valid)}.")

def ask_unique_acc_num(prompt: str, accounts: dict) -> int:
    while True:
        v = ask_positive_int(prompt)
        if v in accounts: print(f"  Account number {v} already exists.")
        else: return v

def ask_unique_cc_num(prompt: str, accounts: dict) -> str:
    used = get_all_cc_nums(accounts)
    while True:
        v = input(prompt).strip()
        if not v:            print("  Credit card number cannot be empty.")
        elif not v.isdigit(): print("  Credit card number must contain digits only.")
        elif v in used:      print(f"  Credit card number '{v}' already in use.")
        else: return v

def ask_unique_vault_no(prompt: str, accounts: dict) -> str:
    used = get_all_vault_nos(accounts)
    while True:
        v = input(prompt).strip()
        if not v:                   print("  Vault number cannot be empty.")
        elif not v.startswith("V"): print("  Vault number must start with 'V' (e.g. V001).")
        elif v in used:             print(f"  Vault number '{v}' already in use.")
        else: return v

def ask_cc_pin(prompt: str) -> str:
    while True:
        v = input(prompt).strip()
        if v.isdigit() and 1 <= int(v) <= 9999: return v
        print("  PIN must be 1–9999 (digits only).")

def ask_non_empty_str(prompt: str) -> str:
    while True:
        v = input(prompt).strip()
        if v: return v
        print("  Cannot be empty.")

def ask_alnum_str(prompt: str) -> str:
    """Ask for a non-empty alphanumeric string (no spaces or special chars)."""
    while True:
        v = input(prompt).strip()
        if not v:              print("  Cannot be empty.")
        elif not v.isalnum(): print("  Must be alphanumeric (letters and digits only, no spaces).")
        else: return v


# ─────────────────────────────────────────────────────────────────────────────
#  Display helpers — tabulate
# ─────────────────────────────────────────────────────────────────────────────

ACCOUNT_HEADERS = ["Acc #", "Type", "Balance", "CC Number / Credit Available", "Vault"]

def _account_row(obj: Account) -> list:
    """Build one table row for an account object."""
    is_cc     = isinstance(obj, CreditCard)
    vault_str = obj.vault._vault_no if obj.vault else "—"
    if is_cc:
        avail   = obj._credit_card_limit - obj._credit_used
        cc_info = f"{obj._credit_card_num}  (avail: ${avail:,.2f})"
    else:
        cc_info = "—"
    return [
        obj._acc_num,
        "Credit Card" if is_cc else "Non-Credit",
        f"${obj._acc_balance:,.2f}",
        cc_info,
        vault_str,
    ]

def print_accounts_table(accounts_list: list, title: str = ""):
    """Print a list of Account objects as a neat tabulate grid."""
    if title:
        print(f"\n  ── {title}  ({len(accounts_list)} found) ──")
    rows = [_account_row(o) for o in accounts_list]
    print(tabulate(rows, headers=ACCOUNT_HEADERS, tablefmt="rounded_outline",
                   colalign=("right", "left", "right", "left", "center")))

def print_single_account(obj: Account):
    """Print a detailed info card for one account."""
    is_cc = isinstance(obj, CreditCard)
    rows  = [
        ["Account Number", obj._acc_num],
        ["Account Type",   "Credit Card" if is_cc else "Non-Credit Card"],
        ["Balance",        f"${obj._acc_balance:,.2f}"],
    ]
    if is_cc:
        avail = obj._credit_card_limit - obj._credit_used
        rows += [
            ["CC Number",         obj._credit_card_num],
            ["Credit Limit",      f"${obj._credit_card_limit:,.2f}"],
            ["Credit Used",       f"${obj._credit_used:,.2f}"],
            ["Credit Available",  f"${avail:,.2f}"],
        ]
    if obj.vault:
        rows += [
            ["Vault Number",  obj.vault._vault_no],
            ["Vault Balance", f"${obj.vault._balance:,.2f}"],
        ]
    else:
        rows.append(["Vault", "None"])
    print(tabulate(rows, tablefmt="rounded_outline"))

def print_log_table(rows: list, title: str = "Account Log"):
    """Print account log entries as a tabulate table."""
    if not rows:
        print("  No log entries found."); return
    print(f"\n  ── {title}  ({len(rows)} entries) ──")
    table = [[r["timestamp"], r["acc_num"], r["action"], r["details"]] for r in rows]
    print(tabulate(table,
                   headers=["Timestamp", "Acc #", "Action", "Details"],
                   tablefmt="rounded_outline",
                   maxcolwidths=[18, 6, 20, 50]))

def get_account_by_input(accounts: dict):
    """Prompt for acc_num, return the Account or None."""
    try:
        num = int(input("  Enter account number: "))
    except ValueError:
        print("  Invalid — must be a whole number.")
        return None
    if num not in accounts:
        print(f"  Account {num} not found.")
        return None
    return accounts[num]


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Modify Account
# ─────────────────────────────────────────────────────────────────────────────

def menu_modify(accounts: dict, data_file: str, log_file: str):
    print("\n  ────────── Modify Account ──────────")
    print("  1. Add account")
    print("  2. Delete account")
    print("  3. Convert: Non-Credit → Credit Card")
    print("  4. Convert: Credit Card → Non-Credit")
    print("  5. Create vault for an account")
    print("  6. Destroy vault of an account")
    print("  7. Back to main menu")
    print("  ─────────────────────────────────────")

    choice = ask_menu_choice(["1","2","3","4","5","6","7"])

    # ── 1. Add account ────────────────────────────────────────────────────────
    if choice == "1":
        print("\n  -- Add New Account --")
        acc_num  = ask_unique_acc_num("  New account number   : ", accounts)
        password = ask_alnum_str    ("  Account password     : ")
        balance  = ask_non_negative_float("  Starting balance ($) : ")
        acc_type = ask_acc_type()

        if acc_type == "credit_card":
            cc_num   = ask_unique_cc_num("  Credit card number   : ", accounts)
            cc_pin   = ask_cc_pin("  Credit card PIN (1-9999): ")
            cc_limit = ask_positive_float("  Credit limit ($)     : ")
            obj      = CreditCard(acc_num, password, balance, cc_num, cc_pin, cc_limit)
        else:
            obj = Non_Credit_Card(acc_num, password, balance)

        if ask_yes_no("  Create a vault? (yes/no): "):
            v_no  = ask_unique_vault_no("  Vault number  : ", accounts)
            v_pwd = ask_alnum_str     ("  Vault password: ")
            obj.vault = Vault(v_no, 0.0, v_pwd)
            append_log(log_file, acc_num, "VAULT_CREATED",
                       f"Vault {v_no} created on account creation")

        accounts[acc_num] = obj
        save_accounts(data_file, accounts)
        append_log(log_file, acc_num, "ACCOUNT_ADDED",
                   f"Type={acc_type}, Balance={balance}")
        print(f"\n  [OK] Account {acc_num} added.")
        print_single_account(obj)

    # ── 2. Delete account ─────────────────────────────────────────────────────
    elif choice == "2":
        print("\n  -- Delete Account --")
        obj = get_account_by_input(accounts)
        if obj is None: return
        print("\n  Account to delete:")
        print_single_account(obj)
        if ask_yes_no("  Confirm deletion? (yes/no): "):
            num = obj._acc_num
            del accounts[num]
            save_accounts(data_file, accounts)
            append_log(log_file, num, "ACCOUNT_DELETED", "Account removed")
            print(f"  [OK] Account {num} deleted.")
        else:
            print("  Deletion cancelled.")

    # ── 3. Non-Credit → Credit ────────────────────────────────────────────────
    elif choice == "3":
        print("\n  -- Convert: Non-Credit → Credit Card --")
        obj = get_account_by_input(accounts)
        if obj is None: return
        if isinstance(obj, CreditCard):
            print("  This account is already a Credit Card account."); return

        cc_num   = ask_unique_cc_num  ("  New credit card number  : ", accounts)
        cc_pin   = ask_cc_pin         ("  Credit card PIN (1-9999) : ")
        cc_limit = ask_positive_float ("  Credit limit ($)        : ")

        new_obj       = CreditCard(obj._acc_num, obj._acc_password,
                                   obj._acc_balance, cc_num, cc_pin, cc_limit)
        new_obj.vault = obj.vault
        accounts[obj._acc_num] = new_obj
        save_accounts(data_file, accounts)
        append_log(log_file, obj._acc_num, "CONVERT_TYPE",
                   f"Changed to credit_card, CC={cc_num}")
        print(f"\n  [OK] Account {obj._acc_num} converted to Credit Card.")
        print_single_account(new_obj)

    # ── 4. Credit → Non-Credit ────────────────────────────────────────────────
    elif choice == "4":
        print("\n  -- Convert: Credit Card → Non-Credit --")
        obj = get_account_by_input(accounts)
        if obj is None: return
        if not isinstance(obj, CreditCard):
            print("  This account is already Non-Credit Card."); return

        new_obj       = Non_Credit_Card(obj._acc_num, obj._acc_password, obj._acc_balance)
        new_obj.vault = obj.vault
        accounts[obj._acc_num] = new_obj
        save_accounts(data_file, accounts)
        append_log(log_file, obj._acc_num, "CONVERT_TYPE",
                   "Changed to non_credit_card, credit card removed")
        print(f"\n  [OK] Account {obj._acc_num} converted to Non-Credit Card.")
        print_single_account(new_obj)

    # ── 5. Create vault ───────────────────────────────────────────────────────
    elif choice == "5":
        print("\n  -- Create Vault --")
        obj = get_account_by_input(accounts)
        if obj is None: return
        if obj.vault:
            print(f"  Account {obj._acc_num} already has vault {obj.vault._vault_no}."); return

        v_no  = ask_unique_vault_no("  New vault number  : ", accounts)
        v_pwd = ask_alnum_str     ("  New vault password: ")
        obj.vault = Vault(v_no, 0.0, v_pwd)
        save_accounts(data_file, accounts)
        append_log(log_file, obj._acc_num, "VAULT_CREATED", f"Vault {v_no} added")
        print(f"\n  [OK] Vault {v_no} created for account {obj._acc_num}.")
        print_single_account(obj)

    # ── 6. Destroy vault ──────────────────────────────────────────────────────
    elif choice == "6":
        print("\n  -- Destroy Vault --")
        obj = get_account_by_input(accounts)
        if obj is None: return
        if not obj.vault:
            print(f"  Account {obj._acc_num} has no vault."); return

        print("\n  Current account / vault info:")
        print_single_account(obj)

        vault_balance = obj.vault._balance
        if not ask_yes_no(f"  Destroy vault {obj.vault._vault_no}? (yes/no): "):
            print("  Cancelled."); return

        if vault_balance > 0:
            print(f"\n  Vault has ${vault_balance:,.2f}. Transfer to:")
            if isinstance(obj, CreditCard):
                print("  1. Account balance")
                print("  2. Credit card (pay back credit)")
                dest = ask_menu_choice(["1","2"])
            else:
                print("  1. Account balance (only option)")
                dest = "1"

            if dest == "1":
                pwd = ask_non_empty_str("  Enter account password to confirm: ")
                if not obj.check_password(pwd):
                    print("  [ERROR] Wrong password. Vault NOT destroyed."); return
                obj._acc_balance += vault_balance
                print(f"  ${vault_balance:,.2f} added to account balance.")
            else:
                pin = ask_non_empty_str("  Enter credit card PIN to confirm: ")
                if not obj.check_cc_pin(pin):
                    print("  [ERROR] Wrong PIN. Vault NOT destroyed."); return
                obj.payback_credit(vault_balance)
                print(f"  ${vault_balance:,.2f} paid back to credit card.")

        v_no = obj.vault._vault_no
        obj.vault = None
        save_accounts(data_file, accounts)
        append_log(log_file, obj._acc_num, "VAULT_DESTROYED",
                   f"Vault {v_no} destroyed, funds=${vault_balance:.2f} transferred")
        print(f"  [OK] Vault {v_no} destroyed.")

    elif choice == "7":
        return


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Show Accounts
# ─────────────────────────────────────────────────────────────────────────────

def menu_show(accounts: dict):
    print("\n  ────────── Show Accounts ──────────")
    print("  1. All accounts")
    print("  2. Credit card accounts")
    print("  3. Non-credit card accounts")
    print("  4. Vault accounts")
    print("  5. Non-vault accounts")
    print("  ───────────────────────────────────")

    choice = ask_menu_choice(["1","2","3","4","5"])
    labels  = {"1": "All Accounts",          "2": "Credit Card Accounts",
               "3": "Non-Credit Accounts",   "4": "Vault Accounts",
               "5": "Non-Vault Accounts"}
    filters = {"1": lambda o: True,
               "2": lambda o: isinstance(o, CreditCard),
               "3": lambda o: isinstance(o, Non_Credit_Card),
               "4": lambda o: o.vault is not None,
               "5": lambda o: o.vault is None}

    filtered = [o for o in accounts.values() if filters[choice](o)]
    if not filtered:
        print("  No accounts found."); return
    print_accounts_table(filtered, labels[choice])


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Account Log
# ─────────────────────────────────────────────────────────────────────────────

def menu_show_log(log_file: str, accounts: dict):
    print("\n  ────────── Account Log ──────────")
    print("  1. Full log")
    print("  2. Log for a particular account")
    print("  ─────────────────────────────────")

    choice = ask_menu_choice(["1","2"])
    rows   = load_log(log_file)
    if not rows:
        print("  No log entries found."); return

    if choice == "2":
        obj = get_account_by_input(accounts)
        if obj is None: return
        rows  = [r for r in rows if r["acc_num"] == str(obj._acc_num)]
        title = f"Account Log — Acc #{obj._acc_num}"
    else:
        title = "Full Account Log"

    print_log_table(rows, title)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n  ======================================")
    print("    Account Management System — File 1  ")
    print("  ======================================\n")

    data_file = input("  Enter account data CSV filename (e.g. account_data.csv) : ").strip()
    if not os.path.exists(data_file):
        print(f"  [ERROR] '{data_file}' not found. Exiting."); return

    log_file = input("  Enter account log CSV filename (e.g. account_log.csv) : ").strip()

    print("\n  [SYSTEM] Loading accounts...")
    accounts = load_accounts(data_file)
    print(f"  [SYSTEM] {len(accounts)} accounts loaded.\n")

    while True:
        print("\n  ════════════ MAIN MENU ════════════")
        print("  1. Modify Account")
        print("  2. Show List")
        print("  3. Show a particular account info")
        print("  4. Show Account Log")
        print("  5. Exit")
        print("  ════════════════════════════════════")

        choice = ask_menu_choice(["1","2","3","4","5"])

        if   choice == "1": menu_modify(accounts, data_file, log_file)
        elif choice == "2": menu_show(accounts)
        elif choice == "3":
            print("\n  -- Account Info --")
            obj = get_account_by_input(accounts)
            if obj: print_single_account(obj)
        elif choice == "4": menu_show_log(log_file, accounts)
        elif choice == "5":
            print("\n  [SYSTEM] Goodbye!\n"); break


if __name__ == "__main__":
    main()
