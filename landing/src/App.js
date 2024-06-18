import React, { useEffect } from "react";
import { Helmet } from "react-helmet";
import { initGA, logPageView } from './analytics';
import useScript from './hooks/useScript';
import CookieConsent from "./components/CookieConsent/CookieConsent";

// Screens
import Landing from "./screens/Landing.jsx";

export default function App() {
  useScript('https://js-eu1.hs-scripts.com/144653709.js', 'prod');

  useEffect(() => {
    initGA();
    logPageView();
  }, []);

  return (
    <>
      <Helmet>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Khula:wght@400;600;800&display=swap" rel="stylesheet" />
      </Helmet>
      <CookieConsent initGA={initGA}/>
      <Landing />
    </>
  );
}

