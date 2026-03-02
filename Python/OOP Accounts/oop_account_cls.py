"""
oop_account_cls2.py
All class definitions for the Account Management & Transaction System.
"""

import datetime


# ─────────────────────────────────────────────────────────────────────────────
#  Lock
# ─────────────────────────────────────────────────────────────────────────────

class Lock:
    def __init__(self, lock_password: str):
        self.lock_password = lock_password

    def __repr__(self):
        return f"Lock(****)"

    def __del__(self):
        pass  # silent destruction


# ─────────────────────────────────────────────────────────────────────────────
#  Vault
# ─────────────────────────────────────────────────────────────────────────────

class Vault:
    def __init__(self, vault_no: str, balance: float, lock_password: str):
        self._vault_no  = vault_no
        self._balance   = float(balance)
        self.lock       = Lock(lock_password)

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def vault_no(self):
        return self._vault_no

    @vault_no.setter
    def vault_no(self, value):
        if value:
            self._vault_no = value
        else:
            print("Invalid vault number.")

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value >= 0:
            self._balance = value
        else:
            print("Vault balance cannot be negative.")

    @property
    def vault_info(self):
        return {
            "vault_no": self._vault_no,
            "balance":  self._balance,
        }

    # ── fund movement ─────────────────────────────────────────────────────────

    def add_funds(self, amount: float):
        """Add money to vault (no destination — internal only)."""
        self._balance += amount

    def deduct_funds(self, amount: float) -> bool:
        """Deduct money from vault. Returns True on success."""
        if amount > self._balance:
            print("[ERROR] Insufficient funds in vault!")
            return False
        self._balance -= amount
        return True

    # ── dunder ────────────────────────────────────────────────────────────────

    def __str__(self):
        return (f"Vault(no={self._vault_no}, "
                f"balance=${self._balance:,.2f})")

    def __repr__(self):
        return f"Vault({self._vault_no!r}, {self._balance})"

    def __del__(self):
        pass  # silent


# ─────────────────────────────────────────────────────────────────────────────
#  Base Account
# ─────────────────────────────────────────────────────────────────────────────

class Account:
    def __init__(self, acc_num: int, acc_password: str, acc_balance: float):
        self._acc_num      = int(acc_num)
        self._acc_password = str(acc_password)
        self._acc_balance  = float(acc_balance)
        self.vault: Vault | None = None          # attached vault (optional)

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def acc_num(self):
        return self._acc_num

    @acc_num.setter
    def acc_num(self, value):
        if int(value) > 0:
            self._acc_num = int(value)
        else:
            print("Invalid account number.")

    @property
    def acc_password(self):
        return self._acc_password

    @acc_password.setter
    def acc_password(self, value):
        if value:
            self._acc_password = value
        else:
            print("Password cannot be empty.")

    @property
    def acc_balance(self):
        return self._acc_balance

    @acc_balance.setter
    def acc_balance(self, value):
        if float(value) >= 0:
            self._acc_balance = float(value)
        else:
            print("Balance cannot be negative.")

    # ── fund movement ─────────────────────────────────────────────────────────

    def add_funds(self, amount: float):
        self._acc_balance += amount

    def deduct_funds(self, amount: float) -> bool:
        if amount > self._acc_balance:
            print("[ERROR] Insufficient account balance!")
            return False
        self._acc_balance -= amount
        return True

    def check_password(self, pwd: str) -> bool:
        return self._acc_password == pwd

    # ── dunder ────────────────────────────────────────────────────────────────

    def __iadd__(self, amount):
        self._acc_balance += amount
        return self

    def __isub__(self, amount):
        if amount > self._acc_balance:
            print("[ERROR] Insufficient funds!")
        else:
            self._acc_balance -= amount
        return self

    def __eq__(self, other):
        if isinstance(other, Account):
            return self._acc_num == other._acc_num
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._acc_num)

    def __contains__(self, item):
        return item in [self._acc_num, self._acc_password, self._acc_balance]

    def __iter__(self):
        return iter([self._acc_num, self._acc_password, self._acc_balance])

    def __getitem__(self, index):
        data = [self._acc_num, self._acc_password, self._acc_balance]
        if 0 <= index < 3:
            return data[index]
        raise IndexError("Index out of range (0=acc_num, 1=password, 2=balance)")

    def __setitem__(self, index, value):
        if   index == 0: self._acc_num      = value
        elif index == 1: self._acc_password = value
        elif index == 2: self._acc_balance  = value
        else: raise IndexError("Index out of range")

    def __repr__(self):
        return f"Account({self._acc_num}, balance={self._acc_balance})"

    def __str__(self):
        return str({"Account Number": self._acc_num,
                    "Account Balance": self._acc_balance})

    def __del__(self):
        pass  # silent


# ─────────────────────────────────────────────────────────────────────────────
#  Non-Credit Card Account
# ─────────────────────────────────────────────────────────────────────────────

class Non_Credit_Card(Account):

    @property
    def non_credit_card_info(self):
        vault_detail = ({"vault_no": self.vault._vault_no,
                         "vault_balance": self.vault._balance}
                        if self.vault else "no vault")
        return {
            "acc_num":     self._acc_num,
            "acc_type":    "non_credit_card",
            "acc_balance": self._acc_balance,
            "vault":       vault_detail,
        }

    def __str__(self):
        return str(self.non_credit_card_info)

    def __repr__(self):
        return f"Non_Credit_Card({self._acc_num}, balance={self._acc_balance})"


# ─────────────────────────────────────────────────────────────────────────────
#  Credit Card Account
# ─────────────────────────────────────────────────────────────────────────────

class CreditCard(Account):
    def __init__(self, acc_num: int, acc_password: str, acc_balance: float,
                 credit_card_num, credit_card_pin, credit_card_limit: float):
        super().__init__(acc_num, acc_password, acc_balance)
        self._credit_card_num   = credit_card_num           # kept as str for leading-zero safety
        self._credit_card_pin   = str(credit_card_pin)
        self._credit_card_limit = float(credit_card_limit)
        self._credit_used       = 0.0                        # track credit usage

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def credit_card_num(self):
        return self._credit_card_num

    @credit_card_num.setter
    def credit_card_num(self, value):
        if value:
            self._credit_card_num = value
        else:
            print("Invalid credit card number.")

    @property
    def credit_card_pin(self):
        return self._credit_card_pin

    @credit_card_pin.setter
    def credit_card_pin(self, value):
        if str(value):
            self._credit_card_pin = str(value)
        else:
            print("Invalid PIN.")

    @property
    def credit_card_limit(self):
        return self._credit_card_limit

    @credit_card_limit.setter
    def credit_card_limit(self, value):
        if float(value) > 0:
            self._credit_card_limit = float(value)
        else:
            print("Credit limit must be positive.")

    @property
    def credit_card_info(self):
        vault_detail = ({"vault_no": self.vault._vault_no,
                         "vault_balance": self.vault._balance}
                        if self.vault else "no vault")
        return {
            "acc_num":          self._acc_num,
            "acc_type":         "credit_card",
            "acc_balance":      self._acc_balance,
            "credit_card_num":  self._credit_card_num,
            "credit_card_limit": self._credit_card_limit,
            "credit_used":      self._credit_used,
            "credit_available": self._credit_card_limit - self._credit_used,
            "vault":            vault_detail,
        }

    # ── credit-card specific fund movement ───────────────────────────────────

    def charge_credit(self, amount: float) -> bool:
        """Charge amount to credit card. Returns True on success."""
        available = self._credit_card_limit - self._credit_used
        if amount > available:
            print("[ERROR] Credit limit exceeded!")
            return False
        if available - amount <= 500:
            print(f"[WARNING] Only ${available - amount:,.2f} credit remaining after this transaction!")
        self._credit_used += amount
        return True

    def payback_credit(self, amount: float):
        """Pay back credit card debt."""
        self._credit_used = max(0.0, self._credit_used - amount)

    def check_cc_pin(self, pin: str) -> bool:
        return self._credit_card_pin == str(pin)

    # ── dunder ────────────────────────────────────────────────────────────────

    def __str__(self):
        return str(self.credit_card_info)

    def __repr__(self):
        return f"CreditCard({self._acc_num}, cc={self._credit_card_num}, balance={self._acc_balance})"

    def __del__(self):
        pass  # silent


# ─────────────────────────────────────────────────────────────────────────────
#  Payment Processor
# ─────────────────────────────────────────────────────────────────────────────

class Payment_Processor:

    def add_funds(self, account_obj: Account, amount: float) -> bool:
        print(f"\n--- [GATEWAY] Adding: ${amount:,.2f} to Account {account_obj.acc_num} ---")
        account_obj.add_funds(amount)
        print(f"[GATEWAY] Success. New Balance: ${account_obj.acc_balance:,.2f}")
        return True

    def deduct_funds(self, account_obj: Account, amount: float) -> bool:
        print(f"\n--- [GATEWAY] Deducting: ${amount:,.2f} from Account {account_obj.acc_num} ---")
        ok = account_obj.deduct_funds(amount)
        if ok:
            print(f"[GATEWAY] Success. New Balance: ${account_obj.acc_balance:,.2f}")
            if account_obj.acc_balance <= 500:
                print(f"[WARNING] Low balance! Only ${account_obj.acc_balance:,.2f} remaining.")
        return ok

    def deduct_via_credit(self, cc_obj: CreditCard, amount: float) -> bool:
        print(f"\n--- [GATEWAY] Charging credit card {cc_obj.credit_card_num}: ${amount:,.2f} ---")
        ok = cc_obj.charge_credit(amount)
        if ok:
            print(f"[GATEWAY] Credit charged. Used: ${cc_obj._credit_used:,.2f} / Limit: ${cc_obj._credit_card_limit:,.2f}")
        return ok

    def transfer_1to1(self, sender: Account, receiver: Account,
                      amount: float, via_credit: bool = False) -> bool:
        print(f"\n--- [GATEWAY] Transfer ${amount:,.2f}: "
              f"Acc {sender.acc_num} → Acc {receiver.acc_num} ---")
        if via_credit:
            if not isinstance(sender, CreditCard):
                print("[ERROR] Sender has no credit card."); return False
            ok = sender.charge_credit(amount)
        else:
            ok = sender.deduct_funds(amount)
        if ok:
            receiver.add_funds(amount)
            if not via_credit:
                if sender.acc_balance <= 500:
                    print(f"[WARNING] Sender low balance: ${sender.acc_balance:,.2f}")
            print(f"[GATEWAY] Transfer successful. Receiver balance: ${receiver.acc_balance:,.2f}")
        return ok

    def transfer_1tomany(self, sender: Account, receivers: list,
                         amount: float, via_credit: bool = False) -> bool:
        print(f"\n--- [GATEWAY] Transfer ${amount:,.2f} each: "
              f"Acc {sender.acc_num} → {len(receivers)} receivers ---")
        for rec in receivers:
            ok = self.transfer_1to1(sender, rec, amount, via_credit)
            if not ok:
                print(f"[GATEWAY] Transfer to Acc {rec.acc_num} failed — stopping.")
                return False
        return True

    def transfer_manyto1(self, senders: list, receiver: Account,
                         amount: float, via_credit: bool = False) -> bool:
        print(f"\n--- [GATEWAY] Transfer ${amount:,.2f} each from "
              f"{len(senders)} senders → Acc {receiver.acc_num} ---")
        for sen in senders:
            ok = self.transfer_1to1(sen, receiver, amount, via_credit)
            if not ok:
                print(f"[GATEWAY] Transfer from Acc {sen.acc_num} failed — stopping.")
                return False
        return True
