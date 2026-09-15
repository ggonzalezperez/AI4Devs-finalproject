import { Navigate, Outlet } from "react-router-dom";
import { useSession } from "../auth/SessionContext";

export default function ProtectedRoute() {
  const { isAuthenticated } = useSession();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
