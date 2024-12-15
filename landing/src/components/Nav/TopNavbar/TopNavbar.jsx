import React, { useEffect, useState } from "react";
import styles from './TopNavbar.module.css';
import { Link } from "react-scroll";
// Components
import Sidebar from "../Sidebar/Sidebar";
import Backdrop from "../../Elements/Backdrop";
// Assets
import LogoIcon from "../../../assets/svg/Logo";
import BurgerIcon from "../../../assets/svg/BurgerIcon";
import FullButton from "../../Buttons/FullButton";

export default function TopNavbar({ handleOpenContactForm }) {
  const [y, setY] = useState(window.scrollY);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [y]);

  return (
    <>
      <Sidebar 
        sidebaropen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen} 
        handleOpenContactForm={handleOpenContactForm} 
      />
      {sidebarOpen && <Backdrop toggleSidebar={setSidebarOpen} />}
      
      <nav 
        className={`${styles.wrapper} flexCenter animate whiteBg`} 
        style={y > 100 ? { height: "60px" } : { height: "80px" }}
      >
        <div className={`${styles.navInner} container flexSpaceCenter`}>
          <LogoIcon />
          <button 
            className={styles.burgerWrapper} 
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <BurgerIcon />
          </button>
          
          <ul className={`${styles.ulWrapper} flexNullCenter`}>
            <li className="semiBold font15 pointer">
              <Link 
                activeClass="active" 
                style={{ padding: "10px 15px" }} 
                to="home" 
                spy={true} 
                smooth={true} 
                offset={-80}
              >
                For HR
              </Link>
            </li>
            <li className="semiBold font15 pointer">
              <Link 
                activeClass="active" 
                style={{ padding: "10px 15px" }} 
                to="jobSeekers" 
                spy={true} 
                smooth={true} 
                offset={-80}
              >
                For Job Seekers
              </Link>
            </li>
            <li className="semiBold font15 pointer">
              <Link 
                activeClass="active" 
                style={{ padding: "10px 15px" }} 
                to="projects" 
                spy={true} 
                smooth={true} 
                offset={-80}
              >
                How it works
              </Link>
            </li>
            <li className="semiBold font15 pointer">
              <Link 
                activeClass="active" 
                style={{ padding: "10px 15px" }} 
                to="contact" 
                spy={true} 
                smooth={true} 
                offset={-80}
              >
                Contact
              </Link>
            </li>
          </ul>
          
          <ul className={`${styles.ulWrapperRight} flexNullCenter`}>
            <li className="semiBold pointer">
              <FullButton title="Get Early Access" action={handleOpenContactForm} />
            </li>
          </ul>
        </div>
      </nav>
    </>
  );
} 