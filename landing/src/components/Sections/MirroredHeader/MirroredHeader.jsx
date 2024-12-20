import React from "react";
import PropTypes from "prop-types";
import styles from "./MirroredHeader.module.css";
// Components
import FullButton from "../../Buttons/FullButton";
// Assets
import HeaderImage from "../../../assets/img/Person is handing their resume to a holographic recruiter.webp";
import QuotesIcon from "../../../assets/svg/Quotes";
import Dots from "../../../assets/svg/Dots";

const MirroredHeader = ({ handleOpenContactForm }) => {
  return (
    <section id="jobSeekers" className={`${styles.wrapper} container flexSpaceCenter mirroredHeader`}>
      <div className={styles.rightSide}>
        <div className={styles.imageWrapper}>
          <img 
            className={`${styles.img} radius8`} 
            src={HeaderImage} 
            alt="office" 
            style={{ zIndex: 9 }} 
          />
          <div className={`${styles.quoteWrapper} flexCenter darkBg radius8`}>
            <div className={styles.quotesWrapper}>
              <QuotesIcon />
            </div>
            <div>
              <p className="font15 whiteColor">
                <em>Success is where preparation and opportunity meet.</em>
              </p>
              <p className="font13 orangeColor textRight" style={{ marginTop: '10px' }}>
                Bobby Unser
              </p>
            </div>
          </div>
          <div className={styles.dotsWrapper}>
            <Dots />
          </div>
        </div>
      </div>
      <div className={`${styles.leftSide} flexCenter`}>
        <div>
          <h1 className="extraBold font60">
            Increase Your Chances of Landing an Interview
          </h1>
          <div className={`${styles.headerP} font13 semiBold`}>
            Use our advanced AI to tailor your resume to job descriptions, boosting your interview prospects.
            Focus more on preparing for interviews and less on manual resume adjustments.
          </div>
          <div className={styles.btnWrapper}>
            <div className={styles.btnWrapper2}>
              <FullButton title="Get Early Access" action={handleOpenContactForm} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

MirroredHeader.propTypes = {
  handleOpenContactForm: PropTypes.func.isRequired,
};

export default MirroredHeader;