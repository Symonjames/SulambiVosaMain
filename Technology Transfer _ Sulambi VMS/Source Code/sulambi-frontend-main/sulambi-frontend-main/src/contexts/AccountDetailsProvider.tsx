import { createContext, ReactNode, useState } from "react";
import { MembershipType } from "../interface/types";

interface AccountDetails {
  username: string;
  accountType: "admin" | "officer" | "member";
  details?: MembershipType;
}

interface Pair {
  accountDetails: AccountDetails;
  setAccountDetails: (state: AccountDetails) => void;
}

export const AccountDetailsContext = createContext<Pair>({
  accountDetails: { username: "", accountType: "admin", details: undefined },
  setAccountDetails: (_state: AccountDetails) => {},
});

const AccountDetailsProvider = ({ children }: { children: ReactNode }) => {
  const [accountDetails, setAccountDetails] = useState<AccountDetails>({
    username: "",
    accountType: localStorage.getItem("accountType") as
      | "admin"
      | "member"
      | "officer",
    details: undefined,
  });

  return (
    <AccountDetailsContext.Provider
      value={{ accountDetails, setAccountDetails }}
    >
      {children}
    </AccountDetailsContext.Provider>
  );
};

export default AccountDetailsProvider;
