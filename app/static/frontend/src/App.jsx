import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Dashboard from "./pages/Dashboard";
import MarketPage from "./pages/MarketPage";
import RoadmapPage from "./pages/RoadmapPage";
import InterviewPage from "./pages/InterviewPage";

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [profile, setProfile] = useState(null);
  const [roadmap, setRoadmap] = useState(null);

  const handleProfileLoaded = (loadedProfile) => {
    setProfile(loadedProfile);
  };

  const handleProfileSaved = (savedProfile) => {
    setProfile(savedProfile);
    setRoadmap(null);
  };

  const handleRoadmapGenerated = (generatedRoadmap) => {
    setRoadmap(generatedRoadmap);
  };

  const renderPage = () => {
    switch (activePage) {
      case "market":
        return <MarketPage />;

      case "roadmap":
        return (
          <RoadmapPage
            profile={profile}
            roadmap={roadmap}
            onRoadmapGenerated={handleRoadmapGenerated}
          />
        );

      case "interview":
        return <InterviewPage />;

      default:
        return (
          <Dashboard
            setActivePage={setActivePage}
            onProfileLoaded={handleProfileLoaded}
            onProfileSaved={handleProfileSaved}
          />
        );
    }
  };

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      <main className="main-content">
        <Topbar activePage={activePage} />

        <div key={activePage} className="page-content">
          {renderPage()}
        </div>
      </main>
    </div>
  );
}

export default App;