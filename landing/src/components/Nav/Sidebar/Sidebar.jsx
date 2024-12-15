import React from "react";
import PropTypes from "prop-types";
import { Link } from "react-scroll";
import styles from "./Sidebar.module.css";
// Assets
import CloseIcon from "../../../assets/svg/CloseIcon";
import LogoIcon from "../../../assets/svg/Logo";
import FullButton from "../../Buttons/FullButton";

export default function Sidebar({ sidebaropen, setSidebarOpen, handleOpenContactForm }) {
  return (
    <nav className={`${styles.wrapper} animate whiteBg`} data-open={sidebaropen}>
      <div className={`${styles.sidebarHeader} flexSpaceCenter`}>
        <div className="flexNullCenter">
          <LogoIcon />
        </div>
        <button 
          onClick={() => setSidebarOpen(false)} 
          className={`${styles.closeBtn} animate pointer`}
        >
          <CloseIcon />
        </button>
      </div>

      <ul className={`${styles.ulStyle} flexNullCenter flexColumn`}>
        <li className="semiBold font15 pointer">
          <Link
            onClick={() => setSidebarOpen(false)}
            activeClass="active"
            style={{ padding: "10px 15px" }}
            to="home"
            spy={true}
            smooth={true}
            offset={-60}
          >
            For HR
          </Link>
        </li>
        <li className="semiBold font15 pointer">
          <Link
            onClick={() => setSidebarOpen(false)}
            activeClass="active"
            style={{ padding: "10px 15px" }}
            to="jobSeekers"
            spy={true}
            smooth={true}
            offset={-60}
          >
            For Job Seekers
          </Link>
        </li>
        <li className="semiBold font15 pointer">
          <Link
            onClick={() => setSidebarOpen(false)}
            activeClass="active"
            style={{ padding: "10px 15px" }}
            to="projects"
            spy={true}
            smooth={true}
            offset={-60}
          >
            How it works
          </Link>
        </li>
        <li className="semiBold font15 pointer">
          <Link
            onClick={() => setSidebarOpen(false)}
            activeClass="active"
            style={{ padding: "10px 15px" }}
            to="contact"
            spy={true}
            smooth={true}
            offset={-60}
          >
            Contact
          </Link>
        </li>
      </ul>
      <ul className={`${styles.ulStyle} flexSpaceCenter flexColumn`}>
        <li className="semiBold font15 pointer flexSpaceCenter">
          <FullButton title="Get Early Access" action={handleOpenContactForm} />
        </li>
      </ul>
    </nav>
  );
}

Sidebar.propTypes = {
  sidebaropen: PropTypes.bool.isRequired,
  setSidebarOpen: PropTypes.func.isRequired,
  handleOpenContactForm: PropTypes.func.isRequired,
}; 