import { createContext, ReactNode, useState, useEffect } from "react";
import { MembershipType } from "../interface/types";
import { getFromSessionObfuscated, saveToSessionObfuscated } from "../utils/storage";
import { getMe } from "../api/auth";

interface AccountDetails {
  username: string;
  accountType: "admin" | "officer" | "member";
  details?: MembershipType;
}

interface Pair {
  accountDetails: AccountDetails;
  setAccountDetails: (state: AccountDetails) => void;
  /** True after /auth/me has been tried (so protected pages know whether to redirect). */
  sessionChecked: boolean;
}

export const AccountDetailsContext = createContext<Pair>({
  accountDetails: { username: "", accountType: "admin", details: undefined },
  setAccountDetails: (_state: AccountDetails) => {},
  sessionChecked: false,
});

const AccountDetailsProvider = ({ children }: { children: ReactNode }) => {
  const [accountDetails, setAccountDetails] = useState<AccountDetails>(() => {
    const saved = getFromSessionObfuscated<AccountDetails>("accountDetails", null);
    if (saved && saved.username && saved.accountType) {
      return {
        username: saved.username,
        accountType: saved.accountType as "admin" | "officer" | "member",
        details: saved.details,
      };
    }
    return { username: "", accountType: "admin", details: undefined };
  });
  const [sessionChecked, setSessionChecked] = useState(false);

  // On mount: if no session cache, try /auth/me (cookie) to restore session.
  // Skip on login page to avoid a 403 in the console (expected when not logged in).
  useEffect(() => {
    if (sessionChecked) return;
    if (accountDetails.username) {
      setSessionChecked(true);
      return;
    }
    const path = typeof window !== "undefined" ? window.location.pathname : "";
    if (path === "/login" || path.endsWith("/login")) {
      setSessionChecked(true);
      return;
    }
    getMe()
      .then((res) => {
        const d = res.data as {
          authenticated?: boolean;
          username?: string;
          accountType?: string;
          memberData?: MembershipType;
        };
        const ok =
          d.authenticated !== false &&
          (d.authenticated === true || Boolean(d.username));
        if (ok && d.username) {
          const next: AccountDetails = {
            username: d.username,
            accountType: (d.accountType as "admin" | "officer" | "member") || "admin",
            details: d.memberData,
          };
          setAccountDetails(next);
          saveToSessionObfuscated("accountDetails", next);
        }
        setSessionChecked(true);
      })
      .catch(() => setSessionChecked(true));
  }, [sessionChecked, accountDetails.username]);

  // Persist to sessionStorage (obfuscated) when accountDetails changes
  useEffect(() => {
    if (accountDetails.username) {
      saveToSessionObfuscated("accountDetails", accountDetails);
    }
  }, [accountDetails]);

  return (
    <AccountDetailsContext.Provider
      value={{ accountDetails, setAccountDetails, sessionChecked }}
    >
      {children}
    </AccountDetailsContext.Provider>
  );
};

export default AccountDetailsProvider;
