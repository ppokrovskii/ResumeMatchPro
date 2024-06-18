import React from 'react';
import Slider from 'react-slick';
import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";
import styles from './Carousel.module.css';
import './Carousel.css';  // for styles from react-slick library

const Carousel = ({ items }) => {
  const settings = {
    dots: true,
    infinite: false,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    centerMode: true,
    centerPadding: '17%', // Adjusted to show part of the next and previous slides
    nextArrow: <SampleNextArrow />,
    prevArrow: <SamplePrevArrow />,
  };

  return (
    <div className={styles.carouselContainer}>
      <Slider {...settings}>
        {items.map((item, index) => (
          <div key={index}>
            <img src={item.image} alt={item.text} className={styles.carouselImage} />
            <p className={styles.carouselText}>{item.text}</p>
          </div>
        ))}
      </Slider>
    </div>
  );
};

const SampleNextArrow = (props) => {
  const { className, style, onClick } = props;
  return (
    <div
      className={`${className} ${styles.arrow} ${styles.arrowNext}`}
      style={{ ...style, display: 'block' }}
      onClick={onClick}
    >
      &gt;
    </div>
  );
};

const SamplePrevArrow = (props) => {
  const { className, style, onClick } = props;
  return (
    <div
      className={`${className} ${styles.arrow} ${styles.arrowPrev}`}
      style={{ ...style, display: 'block' }}
      onClick={onClick}
    >
      &lt;
    </div>
  );
};

export default Carousel;
