import { Link, Outlet, useLocation } from "react-router-dom";

function App() {
  const location = useLocation();
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-xl font-semibold text-rose-300">
            WineLens
          </Link>
          <nav className="flex gap-6 text-sm uppercase tracking-wide text-slate-300">
            <Link className={location.pathname === "/" ? "text-rose-300" : "hover:text-rose-200"} to="/">
              Upload
            </Link>
            <Link className={location.pathname.startsWith("/history") ? "text-rose-300" : "hover:text-rose-200"} to="/history">
              History
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto flex max-w-5xl flex-1 flex-col px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}

export default App;
