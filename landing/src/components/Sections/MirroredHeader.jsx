import React from "react";
import styled from "styled-components";
// Components
import FullButton from "../Buttons/FullButton";
// Assets
import HeaderImage from "../../assets/img/Person is handing their resume to a holographic recruiter.webp";
import QuotesIcon from "../../assets/svg/Quotes";
import Dots from "../../assets/svg/Dots";

export default function MirroredHeader({ handleOpenContactForm }) {
  return (
    <Wrapper id="jobSeekers" className="container flexSpaceCenter mirroredHeader">
      <RightSide>
        <ImageWrapper>
          <Img className="radius8" src={HeaderImage} alt="office" style={{ zIndex: 9 }} />
          <QuoteWrapper className="flexCenter darkBg radius8">
            <QuotesWrapper>
              <QuotesIcon />
            </QuotesWrapper>
            <div>
              <p className="font15 whiteColor">
                <em>Success is where preparation and opportunity meet.</em>
              </p>
              <p className="font13 orangeColor textRight" style={{ marginTop: '10px' }}>Bobby Unser</p>
            </div>
          </QuoteWrapper>
          <DotsWrapper>
            <Dots />
          </DotsWrapper>
        </ImageWrapper>
        {/* <GreyDiv className="lightBg"></GreyDiv> */}
      </RightSide>
      <LeftSide className="flexCenter">
        <div>
          <h1 className="extraBold font60">Increase Your Chances of Landing an Interview</h1>
          <HeaderP className="font13 semiBold">
          Use our advanced AI to tailor your resume to job descriptions, boosting your interview prospects.
Focus more on preparing for interviews and less on manual resume adjustments.
          </HeaderP>
          <BtnWrapper>
            <FullButton title="Get Early Access" action={handleOpenContactForm} />
          </BtnWrapper>
        </div>
      </LeftSide>
    </Wrapper>
  );
}

const Wrapper = styled.section`
  padding-top: 80px;
  width: 100%;
  min-height: 840px;
  @media (max-width: 960px) {
    flex-direction: column;
  }
`;
const LeftSide = styled.div`
  width: 50%;
  height: 100%;
  @media (max-width: 960px) {
    width: 100%;
    order: 2;
    margin: 50px 0;
    text-align: center;
  }
  @media (max-width: 560px) {
    margin: 80px 0 50px 0;
  }
`;
const RightSide = styled.div`
  width: 50%;
  height: 100%;
  @media (max-width: 960px) {
    width: 100%;
    order: 1;
    margin-top: 30px;
  }
`;
const HeaderP = styled.div`
  max-width: 470px;
  padding: 15px 0 50px 0;
  line-height: 1.5rem;
  @media (max-width: 960px) {
    padding: 15px 0 50px 0;
    text-align: center;
    max-width: 100%;
  }
`;
const BtnWrapper = styled.div`
  ${'' /* max-width: 190px; */}
  text-align: right;
  @media (max-width: 960px) {
    margin: 0 auto;
    text-align: center;
  }
`;
// const GreyDiv = styled.div`
//   width: 30%;
//   height: 700px;
//   position: absolute;
//   top: 0;
//   left: 0; /* Changed from right to left */
//   z-index: 0;
//   @media (max-width: 960px) {
//     display: none;
//   }
// `;
const ImageWrapper = styled.div`
  display: flex;
  justify-content: flex-start; /* Changed from flex-end to flex-start */
  position: relative;
  z-index: 9;
  @media (max-width: 960px) {
    width: 100%;
    justify-content: center;
  }
`;
const Img = styled.img`
  @media (max-width: 560px) {
    width: 80%;
    height: auto;
  }
`;
const QuoteWrapper = styled.div`
  position: absolute;
  right: 0; /* Changed from left to right */
  bottom: 50px;
  max-width: 330px;
  padding: 30px;
  z-index: 99;
  @media (max-width: 960px) {
    right: 20px; /* Changed from left to right */
  }
  @media (max-width: 560px) {
    bottom: -50px;
  }
`;
const QuotesWrapper = styled.div`
  position: absolute;
  right: -20px; /* Changed from left to right */
  top: -10px;
`;
const DotsWrapper = styled.div`
  position: absolute;
  left: -100px; /* Changed from right to left */
  bottom: 100px;
  z-index: 2;
  @media (max-width: 960px) {
    left: 100px; /* Changed from right to left */
  }
  @media (max-width: 560px) {
    display: none;
  }
`;
