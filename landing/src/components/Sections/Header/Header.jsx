import React from "react";
import styles from './Header.module.css';
// Components
import FullButton from "../../Buttons/FullButton";
// Assets
import HeaderImage from "../../../assets/img/Successful People in Business Suits Shaking Hands1_mj4.png";
import QuotesIcon from "../../../assets/svg/Quotes";
import Dots from "../../../assets/svg/Dots";

export default function Header({ handleOpenContactForm }) {
  return (
    <section id="home" className={`${styles.wrapper} container flexSpaceCenter`}>
      <div className={`${styles.leftSide} flexCenter`}>
        <div>
          <h1 className="extraBold font60">Speed Up Recruitment with AI-Driven CV Screening</h1>
          <div className={styles.headerP}>
            Leverage our advanced AI to quickly filter and match CVs with job descriptions, streamlining your hiring process.
            Focus more on engaging candidates and less on sifting through CVs.
          </div>
          <div className={styles.btnWrapper}>
            <FullButton title="Get Early Access" action={handleOpenContactForm} />
          </div>
        </div>
      </div>
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
                <em>Leaders of companies that go from good to great start not with 'where' but with 'who.' They start with the people.</em>
              </p>
              <p className="font13 orangeColor textRight" style={{ marginTop: '10px' }}>
                Jim Collins' book "From Good to Great"
              </p>
            </div>
          </div>
          <div className={styles.dotsWrapper}>
            <Dots />
          </div>
        </div>
      </div>
    </section>
  );
} 