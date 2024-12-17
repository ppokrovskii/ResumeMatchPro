import React from "react";
import { Link } from "react-scroll";
import styles from "./Footer.module.css"; // Import the CSS module
// Assets
import LogoImg from "../../../assets/svg/Logo";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={styles.wrapper}>
      <div className="container">
        <div className={`${styles.innerWrapper} flexSpaceCenter`}>
          <Link className="flexCenter animate pointer" to="home" smooth={true} offset={-80}>
            <LogoImg />
            <h1 className={`${styles.logoText} font15 extraBold whiteColor`}>
              {/* Add any text if needed */}
            </h1>
          </Link>
          <p className={`${styles.copyright} font13`}>
            © {currentYear} - <span className="purpleColor font13">
            {/* neoteq.dev */}
            </span> All Rights Reserved
          </p>
          <Link className="animate pointer font13" to="home" smooth={true} offset={-80}>
            Back to top
          </Link>
        </div>
      </div>
    </footer>
  );
} 