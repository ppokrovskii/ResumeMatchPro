import React from "react";
import styled from "styled-components";

export default function FullButton({ title, action, border, borderWidth = "1px", color="#fff", backgroundColor = "#580cd2" }) {
  return (
    <Wrapper
      className="animate pointer radius8"
      onClick={action ? () => action() : null}
      border={border}
      borderWidth={borderWidth}
      color={color}
      style={{ backgroundColor: backgroundColor}}
    >
      {title}
    </Wrapper>
  );
}

const Wrapper = styled.button`
  border: ${(props) => (props.border ? props.borderWidth : "none")};
  background-color: ${(props) => (props.backgroundColor ? props.backgroundColor : "transparent")};
  width: 100%;
  padding: 15px;
  outline: none;
  color: ${(props) => (props.color ? props.color : "#fff")};
  :hover {
    background-color: ${(props) => (props.border ? "transparent" : "#580cd2")};
    border: 1px solid #7620ff;
    color: ${(props) => (props.color ? props.color : "#fff")};
  }
`;

