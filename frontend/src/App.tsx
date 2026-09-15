import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./routes/ProtectedRoute";
import Welcome from "./screens/Welcome";
import CreateFamily from "./screens/CreateFamily";
import Login from "./screens/Login";
import AddExplorer from "./screens/AddExplorer";
import WhoExplores from "./screens/WhoExplores";
import ChildAccess from "./screens/ChildAccess";
import Spark from "./screens/Spark";
import LessonScreen from "./screens/LessonScreen";
import MyKnowledge from "./screens/MyKnowledge";
import AIConfigPanel from "./screens/AIConfigPanel";
import StoryLibrary from "./screens/StoryLibrary";
import StoryReader from "./screens/StoryReader";
import FamilyStories from "./screens/FamilyStories";
import ConnectDevice from "./screens/ConnectDevice";
import ChildAvatar from "./screens/ChildAvatar";
import ChangePassword from "./screens/ChangePassword";
import ResetPassword from "./screens/ResetPassword";
import FamilyLanding from "./screens/FamilyLanding";
import FamilyPanel from "./screens/FamilyPanel";
import ExitChildSession from "./screens/ExitChildSession";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Welcome />} />
      <Route path="/crear" element={<CreateFamily />} />
      <Route path="/login" element={<Login />} />
      <Route path="/recuperar" element={<ResetPassword />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/familia" element={<FamilyLanding />} />
        <Route path="/familia/explorar" element={<WhoExplores />} />
        <Route path="/familia/panel" element={<FamilyPanel />} />
        <Route path="/familia/nuevo" element={<AddExplorer />} />
        <Route path="/explorar/:childId" element={<ChildAccess />} />
        <Route path="/jugar" element={<Spark />} />
        <Route path="/jugar/leccion/:id" element={<LessonScreen />} />
        <Route path="/jugar/mis-islas" element={<MyKnowledge />} />
        <Route path="/jugar/salir" element={<ExitChildSession />} />
        <Route path="/jugar/cuentos" element={<StoryLibrary />} />
        <Route path="/jugar/cuentos/:id" element={<StoryReader />} />
        <Route path="/familia/ia" element={<AIConfigPanel />} />
        <Route path="/familia/cuentos" element={<FamilyStories />} />
        <Route path="/familia/conectar" element={<ConnectDevice />} />
        <Route path="/familia/explorador/:childId" element={<ChildAvatar />} />
        <Route path="/familia/password" element={<ChangePassword />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
