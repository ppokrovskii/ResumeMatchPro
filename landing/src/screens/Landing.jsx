import React from "react";
// Sections
import TopNavbar from "../components/Nav/TopNavbar/TopNavbar";
import ForHR from "../components/Sections/ForHR/ForHR";
import ForJobSeekers from "../components/Sections/ForJobSeekers/ForJobSeekers";
import HowItWorks from "../components/Sections/HowItWorks/HowItWorks";
import Contact from "../components/Sections/Contact/Contact";
import Footer from "../components/Sections/Footer/Footer";
import ContactForm from "../components/ContactForm/ContactForm";
import Notification from "../components/Notification/Notification";
// Custom Hooks
import { useContactForm } from '../hooks/useContactForm';

// Create ContactFormContext
export const ContactFormContext = React.createContext();

// Group components by sections
const PageLayout = ({ children, handleOpenContactForm }) => (
  <>
    <TopNavbar handleOpenContactForm={handleOpenContactForm}/>
    {children}
    <Footer />
  </>
);

const MainContent = ({ handleOpenContactForm }) => (
  <>
    <ForHR handleOpenContactForm={handleOpenContactForm}/>
    <ForJobSeekers handleOpenContactForm={handleOpenContactForm}/>
    <HowItWorks handleOpenContactForm={handleOpenContactForm}/>
    <Contact handleOpenContactForm={handleOpenContactForm}/>
  </>
);

export default function Landing() {
  const { 
    isContactFormOpen, 
    notificationMessage, 
    handleOpenContactForm, 
    handleCloseContactForm, 
    handleSuccessSubmitContactDetails, 
    handleNotificationClose 
  } = useContactForm();

  return (
    <ContactFormContext.Provider value={{ handleOpenContactForm }}>
      <PageLayout handleOpenContactForm={handleOpenContactForm}>
        <ContactForm 
          isOpen={isContactFormOpen} 
          onClose={handleCloseContactForm} 
          onSuccess={handleSuccessSubmitContactDetails}
        />
        {notificationMessage && (
          <Notification 
            message={notificationMessage} 
            onClose={handleNotificationClose} 
          />
        )}
        <MainContent handleOpenContactForm={handleOpenContactForm} />
      </PageLayout>
    </ContactFormContext.Provider>
  );
}


