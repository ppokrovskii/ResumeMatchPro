import Carousel from '../Carousel/Carousel';
import styles from './CarouselWrapper.module.css';
import ProjectImg1 from '../../assets/img/projects/rmp_design1.png';
import ProjectImg2 from '../../assets/img/projects/rmp_design2.png';
import ProjectImg3 from '../../assets/img/projects/rmp_design3.png';

const CarouselWrapper = () => {
  const items = [
    {
      image: ProjectImg1,
      text: 'Upload Your Files'
    },
    {
      image: ProjectImg2,
      text: 'Match CVs to Job Descriptions'
    },
    {
      image: ProjectImg3,
      text: 'Match Job Descriptions to CVs'
    }
  ];

  return (
    <div className={styles.carouselWrapper}>
      <Carousel items={items} />
    </div>
  );
}

export default CarouselWrapper; 