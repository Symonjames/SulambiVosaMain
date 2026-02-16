import { useContext, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { AccountDetailsContext } from "../contexts/AccountDetailsProvider";
import { Box, CircularProgress, Typography } from "@mui/material";

type AccountType = "admin" | "officer" | "member";

interface ProtectedRouteProps {
  /** Only these account types can access. Empty = any logged-in user. */
  allowedRoles?: AccountType[];
}

/**
 * Protects routes so that unauthenticated users are redirected to /login.
 * If allowedRoles is set, only those roles can access (e.g. admin routes only for admin).
 */
const ProtectedRoute = ({ allowedRoles = [] }: ProtectedRouteProps) => {
  const { accountDetails, sessionChecked } = useContext(AccountDetailsContext);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!sessionChecked) return;

    const isLoggedIn = Boolean(accountDetails?.username);
    if (!isLoggedIn) {
      navigate("/login", { state: { from: location.pathname }, replace: true });
      return;
    }

    if (allowedRoles.length > 0) {
      const role = accountDetails?.accountType as AccountType | undefined;
      if (!role || !allowedRoles.includes(role)) {
        navigate("/login", { state: { from: location.pathname }, replace: true });
      }
    }
  }, [sessionChecked, accountDetails?.username, accountDetails?.accountType, allowedRoles, navigate, location.pathname]);

  if (!sessionChecked) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="50vh"
        gap={2}
      >
        <CircularProgress size={48} />
        <Typography color="text.secondary">Checking authentication...</Typography>
      </Box>
    );
  }

  const isLoggedIn = Boolean(accountDetails?.username);
  const role = accountDetails?.accountType as AccountType | undefined;
  const hasAccess = isLoggedIn && (allowedRoles.length === 0 || (role && allowedRoles.includes(role)));

  if (!hasAccess) {
    return null;
  }

  return <Outlet />;
};

export default ProtectedRoute;
