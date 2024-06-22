import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Link } from "react-scroll";
// Assets
import CloseIcon from "../../assets/svg/CloseIcon";
import LogoIcon from "../../assets/svg/Logo";
import FullButton from "../Buttons/FullButton";

export default function Sidebar({ sidebaropen, setSidebarOpen, handleOpenContactForm }) {
  return (
    <Wrapper className="animate whiteBg" $sidebaropen={sidebaropen}>
      <SidebarHeader className="flexSpaceCenter">
        <div className="flexNullCenter">
          <LogoIcon />
          <h1 className="font20" style={{ marginLeft: "15px" }}>
            {/* neoteq.dev */}
          </h1>
        </div>
        <CloseBtn onClick={() => setSidebarOpen((prev) => !prev)} className="animate pointer">
          <CloseIcon />
        </CloseBtn>
      </SidebarHeader>

      <UlStyle className="flexNullCenter flexColumn">
        <li className="semiBold font15 pointer">
          <Link
            onClick={() => setSidebarOpen((prev) => !prev)}
            activeClass="active"
            className=""
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
            onClick={() => setSidebarOpen((prev) => !prev)}
            activeClass="active"
            className=""
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
            onClick={() => setSidebarOpen((prev) => !prev)}
            activeClass="active"
            className=""
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
            onClick={() => setSidebarOpen((prev) => !prev)}
            activeClass="active"
            className=""
            style={{ padding: "10px 15px" }}
            to="contact"
            spy={true}
            smooth={true}
            offset={-60}
          >
            Contact
          </Link>
        </li>
      </UlStyle>
      <UlStyle className="flexSpaceCenter flexColumn">
        {/* <li className="semiBold font15 pointer">
          <a href="/" style={{ padding: "10px 30px 10px 0" }} className="">
            Log in
          </a>
        </li> */}
        <li className="semiBold font15 pointer flexSpaceCenter">
          <FullButton title="Get Early Access" action={handleOpenContactForm} />
        </li>
      </UlStyle>
    </Wrapper>
  );
}

Sidebar.propTypes = {
  sidebaropen: PropTypes.bool.isRequired,
  setSidebarOpen: PropTypes.func.isRequired,
  handleOpenContactForm: PropTypes.func.isRequired,
};

const Wrapper = styled.nav`
  width: 400px;
  height: 100vh;
  position: fixed;
  top: 0;
  padding: 0 30px;
  right: ${(props) => (props.$sidebaropen ? "0px" : "-400px")};
  z-index: 9999;
  transition: right 0.3s ease-in-out;
  @media (max-width: 400px) {
    width: 100%;
  }
`;
const SidebarHeader = styled.div`
  padding: 20px 0;
`;
const CloseBtn = styled.button`
  border: 0px;
  outline: none;
  background-color: transparent;
  padding: 10px;
`;
const UlStyle = styled.ul`
  padding: 40px;
  li {
    margin: 20px 0;
  }
`;
