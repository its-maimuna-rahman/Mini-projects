"""
main2_transaction.py
Transaction System — Main File 2
Handles: add/deduct balance, transfers (1→1, 1→many, many→1),
         vault fund management, credit card payback, transaction log.
Usage: python main2_transaction.py
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

TXN_FIELDNAMES = ["timestamp", "acc_num", "type", "amount", "status", "balance_after"]


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


def append_txn_log(log_file: str, acc_num: int, txn_type: str,
                   amount: float, status: str, balance_after: float):
    """Append one row to the transaction log CSV in append mode —
    permanent audit trail of every dollar moved."""
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
        writer = csv.DictWriter(f, fieldnames=TXN_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp":     timestamp,
            "acc_num":       acc_num,
            "type":          txn_type,
            "amount":        f"{amount:.2f}",
            "status":        status,
            "balance_after": f"{balance_after:.2f}",
        })


# ─────────────────────────────────────────────────────────────────────────────
#  Input-validation helpers
# ─────────────────────────────────────────────────────────────────────────────

def ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(prompt).strip().lower()
        if   ans == "yes": return True
        elif ans == "no":  return False
        else: print("  Invalid — please type 'yes' or 'no'.")

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

def ask_non_empty_str(prompt: str) -> str:
    while True:
        v = input(prompt).strip()
        if v: return v
        print("  Cannot be empty.")

def get_account_by_num(accounts: dict, prompt: str = "  Enter account number: "):
    try:
        num = int(input(prompt))
    except ValueError:
        print("  Invalid — must be a whole number.")
        return None
    if num not in accounts:
        print(f"  Account {num} not found.")
        return None
    return accounts[num]

def pick_multiple_accounts(accounts: dict, exclude_num: int = None) -> list:
    """Let user enter multiple account numbers one by one. Returns list of Account objects."""
    selected, used_nums = [], set()
    print("  Enter account numbers one by one. Type 'done' when finished.")
    while True:
        raw = input(f"  Account #{len(selected)+1} (or 'done'): ").strip().lower()
        if raw == "done":
            if not selected: print("  Must select at least one account."); continue
            break
        try:
            num = int(raw)
        except ValueError:
            print("  Invalid — enter a number or 'done'."); continue
        if num not in accounts:          print(f"  Account {num} not found."); continue
        if exclude_num and num == exclude_num:
            print("  Cannot pick the source account."); continue
        if num in used_nums:             print(f"  Account {num} already selected."); continue
        selected.append(accounts[num])
        used_nums.add(num)
        print(f"  Added account {num}.")
    return selected


# ─────────────────────────────────────────────────────────────────────────────
#  Transfer helpers
# ─────────────────────────────────────────────────────────────────────────────

def choose_transfer_source(sender: Account) -> str:
    """If sender is CreditCard ask balance vs credit, else always 'balance'."""
    if not isinstance(sender, CreditCard):
        return "balance"
    print("\n  Transfer from:")
    print("  1. Account balance")
    print("  2. Credit card")
    return "balance" if ask_menu_choice(["1","2"]) == "1" else "credit"

def authenticate_sender(sender: Account, source: str) -> bool:
    """Authenticate by password (balance) or PIN (credit). Returns True if OK."""
    if source == "balance":
        pwd = ask_non_empty_str("  Enter account password: ")
        if not sender.check_password(pwd):
            print("  [ERROR] Wrong password. Transaction cancelled."); return False
    else:
        pin = ask_non_empty_str("  Enter credit card PIN: ")
        if not sender.check_cc_pin(pin):
            print("  [ERROR] Wrong PIN. Transaction cancelled."); return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
#  Display helpers — tabulate
# ─────────────────────────────────────────────────────────────────────────────

def print_account_card(obj: Account):
    """Compact single-account info panel."""
    is_cc = isinstance(obj, CreditCard)
    rows  = [
        ["Acc #",    obj._acc_num],
        ["Type",     "Credit Card" if is_cc else "Non-Credit Card"],
        ["Balance",  f"${obj._acc_balance:,.2f}"],
    ]
    if is_cc:
        avail = obj._credit_card_limit - obj._credit_used
        rows += [
            ["CC #",             obj._credit_card_num],
            ["Credit Available", f"${avail:,.2f}"],
        ]
    if obj.vault:
        rows.append(["Vault", f"{obj.vault._vault_no}  (${obj.vault._balance:,.2f})"])
    print(tabulate(rows, tablefmt="rounded_outline"))

def print_txn_summary(rows_data: list):
    """Print a tidy transaction result summary table."""
    print(tabulate(rows_data,
                   headers=["Field", "Value"],
                   tablefmt="rounded_outline"))

def print_txn_log_table(log_file: str):
    """Load and display the full transaction log as a table."""
    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        print("  No transaction log entries found."); return
    with open(log_file, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("  No entries."); return
    table = [[r["timestamp"], r["acc_num"], r["type"],
              f"${float(r['amount']):,.2f}", r["status"],
              f"${float(r['balance_after']):,.2f}"] for r in rows]
    print(f"\n  ── Transaction Log  ({len(rows)} entries) ──")
    print(tabulate(table,
                   headers=["Timestamp", "Acc #", "Type", "Amount", "Status", "Balance After"],
                   tablefmt="rounded_outline",
                   colalign=("left","right","left","right","center","right")))


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Transaction
# ─────────────────────────────────────────────────────────────────────────────

def menu_transaction(accounts: dict, data_file: str, log_file: str):
    print("\n  ────────── Transaction ──────────")
    print("  1. Add Balance")
    print("  2. Deduct Balance")
    print("  3. Transfer [1 to 1]")
    print("  4. Transfer [1 to many]")
    print("  5. Transfer [many to 1]")
    print("  6. Back")
    print("  ──────────────────────────────────")

    choice = ask_menu_choice(["1","2","3","4","5","6"])
    if choice == "6": return

    # ── 1. Add Balance ────────────────────────────────────────────────────────
    if choice == "1":
        print("\n  -- Add Balance --")
        obj = get_account_by_num(accounts)
        if obj is None: return
        print_account_card(obj)
        amount = ask_positive_float("  Amount to add ($): ")
        obj.add_funds(amount)
        save_accounts(data_file, accounts)
        append_txn_log(log_file, obj._acc_num, "add", amount, "success", obj._acc_balance)
        print_txn_summary([
            ["Account",     obj._acc_num],
            ["Added",       f"${amount:,.2f}"],
            ["New Balance", f"${obj._acc_balance:,.2f}"],
            ["Status",      "✓ Success"],
        ])

    # ── 2. Deduct Balance ─────────────────────────────────────────────────────
    elif choice == "2":
        print("\n  -- Deduct Balance --")
        obj = get_account_by_num(accounts)
        if obj is None: return
        print_account_card(obj)
        amount = ask_positive_float("  Amount to deduct ($): ")
        ok     = obj.deduct_funds(amount)
        status = "success" if ok else "failed"
        save_accounts(data_file, accounts)
        append_txn_log(log_file, obj._acc_num, "deduct", amount, status, obj._acc_balance)
        print_txn_summary([
            ["Account",     obj._acc_num],
            ["Deducted",    f"${amount:,.2f}"],
            ["New Balance", f"${obj._acc_balance:,.2f}"],
            ["Status",      "✓ Success" if ok else "✗ Failed"],
        ])
        if ok and obj._acc_balance <= 500:
            print(f"  ⚠  [WARNING] Low balance! ${obj._acc_balance:,.2f} remaining.")

    # ── 3. Transfer 1→1 ───────────────────────────────────────────────────────
    elif choice == "3":
        print("\n  -- Transfer [1 to 1] --")
        print("  SENDER:")
        sender = get_account_by_num(accounts)
        if sender is None: return
        print_account_card(sender)

        print("  RECEIVER:")
        receiver = get_account_by_num(accounts)
        if receiver is None: return
        if receiver._acc_num == sender._acc_num:
            print("  Cannot transfer to the same account."); return

        amount = ask_positive_float("  Transfer amount ($): ")
        source = choose_transfer_source(sender)
        if not authenticate_sender(sender, source): return

        ok = sender.charge_credit(amount) if source == "credit" else sender.deduct_funds(amount)
        if ok:
            receiver.add_funds(amount)
            save_accounts(data_file, accounts)
            append_txn_log(log_file, sender._acc_num,   "transfer_out", amount, "success", sender._acc_balance)
            append_txn_log(log_file, receiver._acc_num, "transfer_in",  amount, "success", receiver._acc_balance)
            print_txn_summary([
                ["From",              f"Acc {sender._acc_num}"],
                ["To",                f"Acc {receiver._acc_num}"],
                ["Amount",            f"${amount:,.2f}"],
                ["Via",               "Credit Card" if source == "credit" else "Account Balance"],
                ["Sender Balance",    f"${sender._acc_balance:,.2f}"],
                ["Receiver Balance",  f"${receiver._acc_balance:,.2f}"],
                ["Status",            "✓ Success"],
            ])
            if source == "balance" and sender._acc_balance <= 500:
                print(f"  ⚠  [WARNING] Sender low balance: ${sender._acc_balance:,.2f}")
        else:
            append_txn_log(log_file, sender._acc_num, "transfer_out", amount, "failed", sender._acc_balance)

    # ── 4. Transfer 1→many ────────────────────────────────────────────────────
    elif choice == "4":
        print("\n  -- Transfer [1 to many] --")
        print("  SENDER:")
        sender = get_account_by_num(accounts)
        if sender is None: return
        print_account_card(sender)

        print("\n  RECEIVERS:")
        receivers = pick_multiple_accounts(accounts, exclude_num=sender._acc_num)
        if not receivers: return

        amount = ask_positive_float("  Amount per receiver ($): ")
        source = choose_transfer_source(sender)
        if not authenticate_sender(sender, source): return

        results, all_ok = [], True
        for rec in receivers:
            ok = sender.charge_credit(amount) if source == "credit" else sender.deduct_funds(amount)
            if ok:
                rec.add_funds(amount)
                results.append([f"Acc {rec._acc_num}", f"${amount:,.2f}", "✓ Success",
                                 f"${sender._acc_balance:,.2f}"])
                append_txn_log(log_file, rec._acc_num, "transfer_in",
                               amount, "success", rec._acc_balance)
                if source == "balance" and sender._acc_balance <= 500:
                    print(f"  ⚠  [WARNING] Sender low balance: ${sender._acc_balance:,.2f}")
            else:
                results.append([f"Acc {rec._acc_num}", f"${amount:,.2f}", "✗ Failed",
                                 f"${sender._acc_balance:,.2f}"])
                all_ok = False
                break

        save_accounts(data_file, accounts)
        append_txn_log(log_file, sender._acc_num, "transfer_out_batch",
                       amount, "success" if all_ok else "partial", sender._acc_balance)
        print(f"\n  ── Transfer Results ──")
        print(tabulate(results,
                       headers=["Receiver", "Amount", "Status", "Sender Bal After"],
                       tablefmt="rounded_outline"))

    # ── 5. Transfer many→1 ───────────────────────────────────────────────────
    elif choice == "5":
        print("\n  -- Transfer [many to 1] --")
        print("  SENDERS:")
        senders = pick_multiple_accounts(accounts)
        if not senders: return

        print("  RECEIVER:")
        receiver = get_account_by_num(accounts)
        if receiver is None: return

        amount  = ask_positive_float("  Amount each sender transfers ($): ")
        results = []

        for sen in senders:
            source = choose_transfer_source(sen)
            print(f"  Authenticating Acc {sen._acc_num}...")
            if not authenticate_sender(sen, source):
                results.append([f"Acc {sen._acc_num}", f"${amount:,.2f}", "✗ Auth Failed",
                                 f"${sen._acc_balance:,.2f}"])
                continue
            ok = sen.charge_credit(amount) if source == "credit" else sen.deduct_funds(amount)
            if ok:
                receiver.add_funds(amount)
                results.append([f"Acc {sen._acc_num}", f"${amount:,.2f}", "✓ Success",
                                 f"${sen._acc_balance:,.2f}"])
                append_txn_log(log_file, sen._acc_num, "transfer_out",
                               amount, "success", sen._acc_balance)
                if source == "balance" and sen._acc_balance <= 500:
                    print(f"  ⚠  [WARNING] Acc {sen._acc_num} low balance: ${sen._acc_balance:,.2f}")
            else:
                results.append([f"Acc {sen._acc_num}", f"${amount:,.2f}", "✗ Failed",
                                 f"${sen._acc_balance:,.2f}"])
                append_txn_log(log_file, sen._acc_num, "transfer_out",
                               amount, "failed", sen._acc_balance)

        save_accounts(data_file, accounts)
        append_txn_log(log_file, receiver._acc_num, "transfer_in_batch",
                       0, "done", receiver._acc_balance)
        print(f"\n  ── Transfer Results ──")
        print(tabulate(results,
                       headers=["Sender", "Amount", "Status", "Sender Bal After"],
                       tablefmt="rounded_outline"))
        print(f"\n  Receiver Acc {receiver._acc_num} new balance: ${receiver._acc_balance:,.2f}")


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Manage Vault Balance
# ─────────────────────────────────────────────────────────────────────────────

def menu_vault(accounts: dict, data_file: str, log_file: str):
    print("\n  ────────── Manage Vault Balance ──────────")
    print("  1. Add money to vault")
    print("  2. Deduct money from vault")
    print("  3. Back")
    print("  ──────────────────────────────────────────")

    choice = ask_menu_choice(["1","2","3"])
    if choice == "3": return

    obj = get_account_by_num(accounts)
    if obj is None: return
    if not obj.vault:
        print(f"  Account {obj._acc_num} has no vault."); return

    print_account_card(obj)

    lock_pwd = ask_non_empty_str("  Enter vault lock password: ")
    if lock_pwd != obj.vault.lock.lock_password:
        print("  [ERROR] Wrong vault password."); return

    # ── Add to vault ──────────────────────────────────────────────────────────
    if choice == "1":
        print("  Add from:")
        print("  1. Account balance")
        if isinstance(obj, CreditCard): print("  2. Credit card")
        opts = ["1","2"] if isinstance(obj, CreditCard) else ["1"]
        src  = ask_menu_choice(opts)
        amount = ask_positive_float("  Amount to add to vault ($): ")

        ok = obj.charge_credit(amount) if src == "2" else obj.deduct_funds(amount)
        if ok:
            obj.vault.add_funds(amount)
            save_accounts(data_file, accounts)
            append_txn_log(log_file, obj._acc_num, "vault_add",
                           amount, "success", obj._acc_balance)
            print_txn_summary([
                ["Account",       obj._acc_num],
                ["Added to Vault", f"${amount:,.2f}"],
                ["Via",           "Credit Card" if src == "2" else "Account Balance"],
                ["Vault Balance", f"${obj.vault._balance:,.2f}"],
                ["Acc Balance",   f"${obj._acc_balance:,.2f}"],
                ["Status",        "✓ Success"],
            ])

    # ── Deduct from vault ─────────────────────────────────────────────────────
    elif choice == "2":
        print(f"  Vault balance: ${obj.vault._balance:,.2f}")
        amount = ask_positive_float("  Amount to deduct from vault ($): ")
        print("  Transfer to:")
        print("  1. Account balance")
        if isinstance(obj, CreditCard): print("  2. Credit card (pay back credit)")
        opts = ["1","2"] if isinstance(obj, CreditCard) else ["1"]
        dest = ask_menu_choice(opts)

        ok = obj.vault.deduct_funds(amount)
        if ok:
            if dest == "1": obj.add_funds(amount)
            else:           obj.payback_credit(amount)
            save_accounts(data_file, accounts)
            append_txn_log(log_file, obj._acc_num, "vault_deduct",
                           amount, "success", obj._acc_balance)
            print_txn_summary([
                ["Account",        obj._acc_num],
                ["Deducted from Vault", f"${amount:,.2f}"],
                ["To",             "Account Balance" if dest == "1" else "Credit Card Payback"],
                ["Vault Balance",  f"${obj.vault._balance:,.2f}"],
                ["Acc Balance",    f"${obj._acc_balance:,.2f}"],
                ["Status",         "✓ Success"],
            ])


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Payback Credit Card
# ─────────────────────────────────────────────────────────────────────────────

def menu_payback(accounts: dict, data_file: str, log_file: str):
    print("\n  ────────── Payback Credit Card ──────────")
    print("  1. Via account balance")
    print("  2. Via instant cash")
    print("  3. Back")
    print("  ─────────────────────────────────────────")

    choice = ask_menu_choice(["1","2","3"])
    if choice == "3": return

    obj = get_account_by_num(accounts)
    if obj is None: return
    if not isinstance(obj, CreditCard):
        print("  This account has no credit card."); return

    print_account_card(obj)
    print(f"  Credit used: ${obj._credit_used:,.2f}")

    amount = ask_positive_float("  Amount to pay back ($): ")
    pin    = ask_non_empty_str("  Enter credit card PIN: ")
    if not obj.check_cc_pin(pin):
        print("  [ERROR] Wrong PIN."); return

    if choice == "1":
        ok = obj.deduct_funds(amount)
        if ok:
            obj.payback_credit(amount)
            save_accounts(data_file, accounts)
            append_txn_log(log_file, obj._acc_num, "cc_payback_balance",
                           amount, "success", obj._acc_balance)
            print_txn_summary([
                ["Account",       obj._acc_num],
                ["Paid Back",     f"${amount:,.2f}"],
                ["Via",           "Account Balance"],
                ["Credit Used",   f"${obj._credit_used:,.2f}"],
                ["Acc Balance",   f"${obj._acc_balance:,.2f}"],
                ["Status",        "✓ Success"],
            ])
    elif choice == "2":
        obj.payback_credit(amount)
        save_accounts(data_file, accounts)
        append_txn_log(log_file, obj._acc_num, "cc_payback_cash",
                       amount, "success", obj._acc_balance)
        print_txn_summary([
            ["Account",     obj._acc_num],
            ["Paid Back",   f"${amount:,.2f}"],
            ["Via",         "Instant Cash"],
            ["Credit Used", f"${obj._credit_used:,.2f}"],
            ["Status",      "✓ Success"],
        ])


# ─────────────────────────────────────────────────────────────────────────────
#  Sub-menu: Show Transaction Log
# ─────────────────────────────────────────────────────────────────────────────

def menu_show_txn_log(log_file: str):
    print("\n  ────────── Show Transaction Log ──────────")
    print("  1. Full log")
    print("  2. Log for a particular account")
    print("  ───────────────────────────────────────────")
    choice = ask_menu_choice(["1", "2"])
    if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
        print("  No transaction log entries found."); return
    with open(log_file, newline="") as f:
        rows = list(csv.DictReader(f))
    rows = [r for r in rows if all(k in r and r[k] is not None for k in TXN_FIELDNAMES)]
    if not rows:
        print("  No transaction log entries found."); return
    if choice == "2":
        try:
            num = int(input("  Enter account number: "))
        except ValueError:
            print("  Invalid — must be a whole number."); return
        rows = [r for r in rows if r["acc_num"] == str(num)]
        if not rows:
            print(f"  No log entries found for account {num}."); return
        title = f"Transaction Log — Acc #{num}"
    else:
        title = "Full Transaction Log"
    table = [[r["timestamp"], r["acc_num"], r["type"],
              f"${float(r['amount']):,.2f}", r["status"],
              f"${float(r['balance_after']):,.2f}"] for r in rows]
    print(f"\n  ── {title}  ({len(rows)} entries) ──")
    print(tabulate(table,
                   headers=["Timestamp", "Acc #", "Type", "Amount", "Status", "Balance After"],
                   tablefmt="rounded_outline",
                   colalign=("left","right","left","right","center","right")))


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n  ======================================")
    print("    Transaction System — File 2         ")
    print("  ======================================\n")

    data_file = input("  Enter account data CSV filename  (e.g. account_data.csv)     : ").strip()
    if not os.path.exists(data_file):
        print(f"  [ERROR] '{data_file}' not found. Exiting."); return

    log_file = input("  Enter transaction log CSV filename (e.g. transaction_log.csv)  : ").strip()

    print("\n  [SYSTEM] Loading accounts...")
    accounts = load_accounts(data_file)
    print(f"  [SYSTEM] {len(accounts)} accounts loaded.\n")

    while True:
        print("\n  ════════════ MAIN MENU ════════════")
        print("  1. Transaction")
        print("  2. Manage Vault Balance")
        print("  3. Payback Credit Card")
        print("  4. Show Transaction Log")
        print("  5. Exit")
        print("  ════════════════════════════════════")

        choice = ask_menu_choice(["1","2","3","4","5"])

        if   choice == "1": menu_transaction(accounts, data_file, log_file)
        elif choice == "2": menu_vault(accounts, data_file, log_file)
        elif choice == "3": menu_payback(accounts, data_file, log_file)
        elif choice == "4": menu_show_txn_log(log_file)
        elif choice == "5":
            print("\n  [SYSTEM] Goodbye!\n"); break


if __name__ == "__main__":
    main()
