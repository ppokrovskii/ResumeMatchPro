import React from "react";
// Sections
import TopNavbar from "../components/Nav/TopNavbar/TopNavbar";
import Header from "../components/Sections/Header/Header";
import MirroredHeader from "../components/Sections/MirroredHeader";
// import Services from "../components/Sections/Services";
import Projects from "../components/Sections/Projects";
// import HowItWorks from "../components/Sections/HowItWorks/HowItWorks";
// import Blog from "../components/Sections/Blog";
// import Pricing from "../components/Sections/Pricing";
import Contact from "../components/Sections/Contact/Contact";
import Footer from "../components/Sections/Footer"
import ContactForm from "../components/ContactForm/ContactForm";
import Notification from "../components/Notification/Notification";


export default function Landing() {
  const [isContactFormOpen, setIsContactFormOpen] = React.useState(false);
  const [notificationMessage, setNotificationMessage] = React.useState('');

  const handleOpenContactForm = () => {
    setIsContactFormOpen(true);
  };

  const handleCloseContactForm = () => {
    setIsContactFormOpen(false);
  };

  const handleSuccessSubmitContactDetails = (message) => {
    debugger;
    setNotificationMessage(message);
    handleCloseContactForm();
  };

  const handleNotificationClose = () => {
    setNotificationMessage('');
  }


  return (
    <>
      <TopNavbar handleOpenContactForm={handleOpenContactForm}/>
      <ContactForm isOpen={isContactFormOpen} onClose={handleCloseContactForm} onSuccess={handleSuccessSubmitContactDetails}/>
      {notificationMessage && (
        <Notification message={notificationMessage} onClose={handleNotificationClose} />
      )}
      <Header handleOpenContactForm={handleOpenContactForm}/>
      <MirroredHeader handleOpenContactForm={handleOpenContactForm}/>
      {/* <Services handleOpenContactForm={handleOpenContactForm}/> */}
      <Projects handleOpenContactForm={handleOpenContactForm}/>
      {/* {HowItWorks} */}
      {/* <Blog /> */}
      {/* <Pricing /> */}
      <Contact handleOpenContactForm={handleOpenContactForm}/>
      <Footer />
    </>
  );
}


