import React from "react";
import styled from "styled-components";

export default function FullButton({ title, action, border, borderWidth = "1px", color = "#fff", backgroundColor = "#580cd2" }) {
  return (
    <Wrapper
      className="animate pointer"
      onClick={action ? () => action() : null}
      $border={border}
      $borderWidth={borderWidth}
      $color={color}
      $backgroundColor={backgroundColor}
    >
      {title}
    </Wrapper>
  );
}

const Wrapper = styled.button`
  border: ${(props) => (props.$border ? props.$border : "none")};
  background-color: ${(props) => (props.$backgroundColor ? props.$backgroundColor : "transparent")};
  border-radius: 12px;
  max-width: 50vw;
  width: 100%;
  padding: 1vw 2vw;
  outline: none;
  color: ${(props) => (props.$color ? props.$color : "#fff")};
  font-size: 16px;
  
  :hover {
    background-color: ${(props) => (props.$border ? "transparent" : "#580cd2")};
    border: 1px solid #7620ff;
    color: ${(props) => (props.$color ? props.$color : "#fff")};
  }

  @media (max-width: 768px) {
    font-size: 14px;
    padding: 12px;
  }

  @media (max-width: 480px) {
    font-size: 12px;
    padding: 10px;
    max-width: 180px;
  }
`;
